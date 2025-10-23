"""
Real-Time Sentiment Analysis System
Analiza sentimiento de Twitter, Reddit, News en tiempo real
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import numpy as np
from loguru import logger
import re
from textblob import TextBlob
import json


class SentimentAnalyzer:
    """
    Analizador de sentimiento multi-fuente
    
    Fuentes:
    - Twitter (API v2)
    - Reddit (PRAW)
    - News (NewsAPI, Finnhub)
    - Telegram (opcional)
    
    Salida: Sentiment score de -1 (muy negativo) a +1 (muy positivo)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # APIs
        self.twitter_bearer = config.get('twitter_bearer_token')
        self.news_api_key = config.get('news_api_key')
        self.finnhub_api_key = config.get('finnhub_api_key')
        
        # Buffers de sentimiento
        self.twitter_buffer = deque(maxlen=1000)
        self.reddit_buffer = deque(maxlen=1000)
        self.news_buffer = deque(maxlen=500)
        
        # Pesos por fuente
        self.weights = {
            'twitter': 0.3,
            'reddit': 0.3,
            'news': 0.4
        }
        
        # Cache
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        logger.info("Sentiment Analyzer inicializado")
    
    async def analyze_twitter(self, query: str, max_results: int = 100) -> Dict:
        """
        Analiza sentimiento de Twitter
        
        Args:
            query: Query de búsqueda (ej: "BTC OR Bitcoin")
            max_results: Máximo de tweets
        
        Returns:
            Dict con sentimiento agregado
        """
        if not self.twitter_bearer:
            logger.warning("Twitter API no configurado")
            return {'sentiment': 0.0, 'count': 0}
        
        try:
            # Twitter API v2
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer}"}
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,lang"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Twitter API error: {response.status}")
                        return {'sentiment': 0.0, 'count': 0}
                    
                    data = await response.json()
                    tweets = data.get('data', [])
            
            # Analizar sentimiento de cada tweet
            sentiments = []
            
            for tweet in tweets:
                text = tweet.get('text', '')
                
                # Limpiar texto
                text = self._clean_text(text)
                
                # Analizar sentimiento
                sentiment = self._analyze_text_sentiment(text)
                
                # Ponderar por engagement
                metrics = tweet.get('public_metrics', {})
                likes = metrics.get('like_count', 0)
                retweets = metrics.get('retweet_count', 0)
                weight = 1 + np.log1p(likes + retweets * 2)  # Retweets valen más
                
                sentiments.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'timestamp': tweet.get('created_at'),
                    'text': text[:100]
                })
                
                # Guardar en buffer
                self.twitter_buffer.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'timestamp': datetime.now()
                })
            
            # Calcular sentimiento ponderado
            if sentiments:
                total_weight = sum(s['weight'] for s in sentiments)
                weighted_sentiment = sum(s['sentiment'] * s['weight'] for s in sentiments) / total_weight
            else:
                weighted_sentiment = 0.0
            
            result = {
                'sentiment': weighted_sentiment,
                'count': len(sentiments),
                'source': 'twitter',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Twitter Sentiment: {weighted_sentiment:.3f} ({len(sentiments)} tweets)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en Twitter analysis: {e}")
            return {'sentiment': 0.0, 'count': 0}
    
    async def analyze_reddit(self, subreddit: str, query: str, limit: int = 100) -> Dict:
        """
        Analiza sentimiento de Reddit
        
        Args:
            subreddit: Subreddit (ej: "cryptocurrency")
            query: Query de búsqueda
            limit: Límite de posts
        
        Returns:
            Dict con sentimiento agregado
        """
        try:
            # Reddit API (sin autenticación, solo lectura)
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                "q": query,
                "limit": limit,
                "sort": "new",
                "restrict_sr": "on"
            }
            headers = {"User-Agent": "TradingBot/1.0"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Reddit API error: {response.status}")
                        return {'sentiment': 0.0, 'count': 0}
                    
                    data = await response.json()
                    posts = data.get('data', {}).get('children', [])
            
            sentiments = []
            
            for post in posts:
                post_data = post.get('data', {})
                
                # Título y texto
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                text = f"{title} {selftext}"
                
                # Limpiar
                text = self._clean_text(text)
                
                # Analizar
                sentiment = self._analyze_text_sentiment(text)
                
                # Ponderar por score
                score = post_data.get('score', 0)
                num_comments = post_data.get('num_comments', 0)
                weight = 1 + np.log1p(score + num_comments)
                
                sentiments.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'timestamp': post_data.get('created_utc'),
                    'text': text[:100]
                })
                
                # Buffer
                self.reddit_buffer.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'timestamp': datetime.now()
                })
            
            # Calcular ponderado
            if sentiments:
                total_weight = sum(s['weight'] for s in sentiments)
                weighted_sentiment = sum(s['sentiment'] * s['weight'] for s in sentiments) / total_weight
            else:
                weighted_sentiment = 0.0
            
            result = {
                'sentiment': weighted_sentiment,
                'count': len(sentiments),
                'source': 'reddit',
                'subreddit': subreddit,
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Reddit Sentiment: {weighted_sentiment:.3f} ({len(sentiments)} posts)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en Reddit analysis: {e}")
            return {'sentiment': 0.0, 'count': 0}
    
    async def analyze_news(self, query: str, hours_back: int = 24) -> Dict:
        """
        Analiza sentimiento de noticias
        
        Args:
            query: Query (ej: "Bitcoin")
            hours_back: Horas hacia atrás
        
        Returns:
            Dict con sentimiento agregado
        """
        if not self.news_api_key:
            logger.warning("News API no configurado")
            return {'sentiment': 0.0, 'count': 0}
        
        try:
            # NewsAPI
            url = "https://newsapi.org/v2/everything"
            from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            params = {
                "q": query,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": self.news_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"News API error: {response.status}")
                        return {'sentiment': 0.0, 'count': 0}
                    
                    data = await response.json()
                    articles = data.get('articles', [])
            
            sentiments = []
            
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                text = f"{title} {description}"
                
                # Limpiar
                text = self._clean_text(text)
                
                # Analizar
                sentiment = self._analyze_text_sentiment(text)
                
                # Peso por fuente (algunas fuentes son más confiables)
                source = article.get('source', {}).get('name', '')
                weight = self._get_source_weight(source)
                
                sentiments.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'source': source,
                    'timestamp': article.get('publishedAt'),
                    'text': text[:100]
                })
                
                # Buffer
                self.news_buffer.append({
                    'sentiment': sentiment,
                    'weight': weight,
                    'timestamp': datetime.now()
                })
            
            # Calcular ponderado
            if sentiments:
                total_weight = sum(s['weight'] for s in sentiments)
                weighted_sentiment = sum(s['sentiment'] * s['weight'] for s in sentiments) / total_weight
            else:
                weighted_sentiment = 0.0
            
            result = {
                'sentiment': weighted_sentiment,
                'count': len(sentiments),
                'source': 'news',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"News Sentiment: {weighted_sentiment:.3f} ({len(sentiments)} articles)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en News analysis: {e}")
            return {'sentiment': 0.0, 'count': 0}
    
    async def get_aggregated_sentiment(self, symbol: str) -> Dict:
        """
        Obtiene sentimiento agregado de todas las fuentes
        
        Args:
            symbol: Símbolo (ej: "BTC", "BTCUSDT")
        
        Returns:
            Dict con sentimiento agregado y desglose
        """
        # Preparar queries
        queries = self._prepare_queries(symbol)
        
        # Analizar todas las fuentes en paralelo
        twitter_task = self.analyze_twitter(queries['twitter'])
        reddit_task = self.analyze_reddit("cryptocurrency", queries['reddit'])
        news_task = self.analyze_news(queries['news'])
        
        twitter_result, reddit_result, news_result = await asyncio.gather(
            twitter_task, reddit_task, news_task,
            return_exceptions=True
        )
        
        # Manejar errores
        if isinstance(twitter_result, Exception):
            twitter_result = {'sentiment': 0.0, 'count': 0}
        if isinstance(reddit_result, Exception):
            reddit_result = {'sentiment': 0.0, 'count': 0}
        if isinstance(news_result, Exception):
            news_result = {'sentiment': 0.0, 'count': 0}
        
        # Calcular sentimiento agregado ponderado
        total_weight = 0
        weighted_sum = 0
        
        sources = {
            'twitter': twitter_result,
            'reddit': reddit_result,
            'news': news_result
        }
        
        for source, result in sources.items():
            if result['count'] > 0:
                weight = self.weights[source]
                weighted_sum += result['sentiment'] * weight
                total_weight += weight
        
        aggregated_sentiment = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Calcular momentum (cambio en sentimiento)
        momentum = self._calculate_sentiment_momentum()
        
        # Clasificar sentimiento
        classification = self._classify_sentiment(aggregated_sentiment)
        
        result = {
            'symbol': symbol,
            'aggregated_sentiment': aggregated_sentiment,
            'classification': classification,
            'momentum': momentum,
            'sources': {
                'twitter': {
                    'sentiment': twitter_result['sentiment'],
                    'count': twitter_result['count']
                },
                'reddit': {
                    'sentiment': reddit_result['sentiment'],
                    'count': reddit_result['count']
                },
                'news': {
                    'sentiment': news_result['sentiment'],
                    'count': news_result['count']
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Aggregated Sentiment for {symbol}: {aggregated_sentiment:.3f} ({classification})")
        
        return result
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analiza sentimiento de un texto usando TextBlob
        
        Returns:
            Sentiment score de -1 a +1
        """
        if not text:
            return 0.0
        
        try:
            blob = TextBlob(text)
            # TextBlob retorna -1 a +1
            sentiment = blob.sentiment.polarity
            return sentiment
        except:
            return 0.0
    
    def _clean_text(self, text: str) -> str:
        """Limpia texto"""
        # Remover URLs
        text = re.sub(r'http\S+', '', text)
        # Remover menciones
        text = re.sub(r'@\w+', '', text)
        # Remover hashtags (mantener texto)
        text = re.sub(r'#(\w+)', r'\1', text)
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _prepare_queries(self, symbol: str) -> Dict:
        """Prepara queries para cada fuente"""
        # Mapeo de símbolos
        symbol_map = {
            'BTC': ['Bitcoin', 'BTC'],
            'ETH': ['Ethereum', 'ETH'],
            'BTCUSDT': ['Bitcoin', 'BTC'],
            'ETHUSDT': ['Ethereum', 'ETH']
        }
        
        keywords = symbol_map.get(symbol.upper(), [symbol])
        
        return {
            'twitter': ' OR '.join(keywords),
            'reddit': ' '.join(keywords),
            'news': keywords[0]
        }
    
    def _get_source_weight(self, source: str) -> float:
        """Peso por fuente de noticias"""
        # Fuentes más confiables tienen mayor peso
        weights = {
            'Bloomberg': 2.0,
            'Reuters': 2.0,
            'Financial Times': 1.8,
            'Wall Street Journal': 1.8,
            'CNBC': 1.5,
            'CoinDesk': 1.5,
            'Cointelegraph': 1.3
        }
        return weights.get(source, 1.0)
    
    def _calculate_sentiment_momentum(self) -> float:
        """
        Calcula momentum del sentimiento
        Compara sentimiento reciente vs anterior
        """
        # Últimos 10 minutos vs 10 minutos anteriores
        now = datetime.now()
        recent_cutoff = now - timedelta(minutes=10)
        older_cutoff = now - timedelta(minutes=20)
        
        recent_sentiments = []
        older_sentiments = []
        
        # Twitter
        for item in self.twitter_buffer:
            if item['timestamp'] > recent_cutoff:
                recent_sentiments.append(item['sentiment'])
            elif item['timestamp'] > older_cutoff:
                older_sentiments.append(item['sentiment'])
        
        # Reddit
        for item in self.reddit_buffer:
            if item['timestamp'] > recent_cutoff:
                recent_sentiments.append(item['sentiment'])
            elif item['timestamp'] > older_cutoff:
                older_sentiments.append(item['sentiment'])
        
        # News
        for item in self.news_buffer:
            if item['timestamp'] > recent_cutoff:
                recent_sentiments.append(item['sentiment'])
            elif item['timestamp'] > older_cutoff:
                older_sentiments.append(item['sentiment'])
        
        if recent_sentiments and older_sentiments:
            recent_avg = np.mean(recent_sentiments)
            older_avg = np.mean(older_sentiments)
            momentum = recent_avg - older_avg
        else:
            momentum = 0.0
        
        return momentum
    
    def _classify_sentiment(self, sentiment: float) -> str:
        """Clasifica sentimiento en categorías"""
        if sentiment > 0.5:
            return "VERY_BULLISH"
        elif sentiment > 0.2:
            return "BULLISH"
        elif sentiment > -0.2:
            return "NEUTRAL"
        elif sentiment > -0.5:
            return "BEARISH"
        else:
            return "VERY_BEARISH"
    
    def get_sentiment_history(self, source: str = 'all', minutes: int = 60) -> List[Dict]:
        """
        Obtiene historial de sentimiento
        
        Args:
            source: 'twitter', 'reddit', 'news', 'all'
            minutes: Minutos hacia atrás
        
        Returns:
            Lista de sentimientos históricos
        """
        cutoff = datetime.now() - timedelta(minutes=minutes)
        history = []
        
        buffers = {
            'twitter': self.twitter_buffer,
            'reddit': self.reddit_buffer,
            'news': self.news_buffer
        }
        
        if source == 'all':
            for buf_name, buf in buffers.items():
                for item in buf:
                    if item['timestamp'] > cutoff:
                        history.append({
                            'source': buf_name,
                            'sentiment': item['sentiment'],
                            'timestamp': item['timestamp'].isoformat()
                        })
        else:
            buf = buffers.get(source)
            if buf:
                for item in buf:
                    if item['timestamp'] > cutoff:
                        history.append({
                            'source': source,
                            'sentiment': item['sentiment'],
                            'timestamp': item['timestamp'].isoformat()
                        })
        
        return sorted(history, key=lambda x: x['timestamp'])
