"""
Multi-Agent Coordinator System
6 agentes especializados trabajando juntos para decisiones óptimas
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import asyncio


class AgentType(Enum):
    """Tipos de agentes especializados"""
    PREDICTOR = "predictor"
    RISK_MANAGER = "risk_manager"
    PORTFOLIO_MANAGER = "portfolio_manager"
    REGIME_DETECTOR = "regime_detector"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    EXECUTION_OPTIMIZER = "execution_optimizer"


class Decision(Enum):
    """Decisiones posibles"""
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class AgentVote:
    """Voto de un agente"""
    agent_type: AgentType
    decision: Decision
    confidence: float  # 0-1
    reasoning: str
    metrics: Dict


class MultiAgentCoordinator:
    """
    Coordinador de Multi-Agentes
    
    Arquitectura:
    - 6 agentes especializados
    - Voting mechanism (ponderado por confianza)
    - Conflict resolution
    - Performance tracking por agente
    - Adaptive weighting (mejores agentes tienen más peso)
    """
    
    def __init__(self):
        # Pesos iniciales (se adaptan según performance)
        self.agent_weights = {
            AgentType.PREDICTOR: 0.25,
            AgentType.RISK_MANAGER: 0.20,
            AgentType.PORTFOLIO_MANAGER: 0.15,
            AgentType.REGIME_DETECTOR: 0.15,
            AgentType.SENTIMENT_ANALYZER: 0.15,
            AgentType.EXECUTION_OPTIMIZER: 0.10
        }
        
        # Performance tracking
        self.agent_performance = {
            agent_type: {
                'correct_predictions': 0,
                'total_predictions': 0,
                'accuracy': 0.5,
                'sharpe_contribution': 0.0
            }
            for agent_type in AgentType
        }
        
        # Historial de decisiones
        self.decision_history = []
        
        # Configuración
        self.min_confidence_threshold = 0.3
        self.consensus_threshold = 0.6
        self.max_history = 1000
        
        logger.info("Multi-Agent Coordinator inicializado con 6 agentes")
    
    async def get_collective_decision(
        self,
        market_data: Dict,
        portfolio_state: Dict,
        sentiment_data: Dict
    ) -> Dict:
        """
        Obtiene decisión colectiva de todos los agentes
        
        Args:
            market_data: Datos de mercado (precio, volumen, indicadores)
            portfolio_state: Estado del portfolio (balance, posiciones)
            sentiment_data: Datos de sentimiento
        
        Returns:
            Dict con decisión final y desglose
        """
        # Recolectar votos de todos los agentes en paralelo
        votes = await self._collect_votes(market_data, portfolio_state, sentiment_data)
        
        # Calcular decisión agregada
        final_decision = self._aggregate_votes(votes)
        
        # Detectar conflictos
        conflicts = self._detect_conflicts(votes)
        
        # Resolver conflictos si existen
        if conflicts:
            final_decision = self._resolve_conflicts(votes, conflicts, final_decision)
        
        # Calcular confianza colectiva
        collective_confidence = self._calculate_collective_confidence(votes, final_decision)
        
        # Preparar resultado
        result = {
            'decision': final_decision['decision'],
            'confidence': collective_confidence,
            'position_size': final_decision.get('position_size', 0.0),
            'votes': [
                {
                    'agent': vote.agent_type.value,
                    'decision': vote.decision.value,
                    'confidence': vote.confidence,
                    'reasoning': vote.reasoning
                }
                for vote in votes
            ],
            'conflicts': conflicts,
            'consensus_level': self._calculate_consensus(votes),
            'timestamp': market_data.get('timestamp')
        }
        
        # Guardar en historial
        self._save_to_history(result)
        
        logger.info(f"Decisión colectiva: {final_decision['decision'].name} "
                   f"(confianza: {collective_confidence:.2f}, "
                   f"consenso: {result['consensus_level']:.2f})")
        
        return result
    
    async def _collect_votes(
        self,
        market_data: Dict,
        portfolio_state: Dict,
        sentiment_data: Dict
    ) -> List[AgentVote]:
        """Recolecta votos de todos los agentes"""
        
        # Ejecutar agentes en paralelo
        tasks = [
            self._predictor_agent_vote(market_data),
            self._risk_manager_agent_vote(market_data, portfolio_state),
            self._portfolio_manager_agent_vote(portfolio_state, market_data),
            self._regime_detector_agent_vote(market_data),
            self._sentiment_analyzer_agent_vote(sentiment_data, market_data),
            self._execution_optimizer_agent_vote(market_data, portfolio_state)
        ]
        
        votes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar errores
        valid_votes = [v for v in votes if isinstance(v, AgentVote)]
        
        return valid_votes
    
    async def _predictor_agent_vote(self, market_data: Dict) -> AgentVote:
        """
        Agente Predictor: Predice precio futuro
        Usa ensemble de modelos de IA
        """
        try:
            # Extraer features
            price = market_data.get('close', 0)
            features = market_data.get('features', [])
            
            # Predicción (simulada - integrar con tu AdvancedPredictor)
            # En producción: prediction = self.predictor.predict(features)
            price_change = np.random.normal(0.001, 0.02)  # Simulación
            predicted_price = price * (1 + price_change)
            
            # Decisión basada en predicción
            if price_change > 0.02:
                decision = Decision.STRONG_BUY
                confidence = min(abs(price_change) * 20, 0.95)
            elif price_change > 0.005:
                decision = Decision.BUY
                confidence = min(abs(price_change) * 15, 0.85)
            elif price_change < -0.02:
                decision = Decision.STRONG_SELL
                confidence = min(abs(price_change) * 20, 0.95)
            elif price_change < -0.005:
                decision = Decision.SELL
                confidence = min(abs(price_change) * 15, 0.85)
            else:
                decision = Decision.HOLD
                confidence = 0.5
            
            return AgentVote(
                agent_type=AgentType.PREDICTOR,
                decision=decision,
                confidence=confidence,
                reasoning=f"Predicción: ${predicted_price:.2f} ({price_change*100:+.2f}%)",
                metrics={
                    'predicted_price': predicted_price,
                    'price_change': price_change,
                    'current_price': price
                }
            )
        except Exception as e:
            logger.error(f"Error en Predictor Agent: {e}")
            return AgentVote(
                agent_type=AgentType.PREDICTOR,
                decision=Decision.HOLD,
                confidence=0.0,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    async def _risk_manager_agent_vote(
        self,
        market_data: Dict,
        portfolio_state: Dict
    ) -> AgentVote:
        """
        Agente Risk Manager: Evalúa riesgo
        Usa VaR, CVaR, drawdown
        """
        try:
            # Estado del portfolio
            current_drawdown = portfolio_state.get('drawdown', 0)
            var_95 = portfolio_state.get('var_95', 0)
            daily_loss = portfolio_state.get('daily_loss', 0)
            
            # Volatilidad actual
            volatility = market_data.get('volatility', 0.02)
            
            # Evaluar riesgo
            risk_score = 0
            
            # Penalizar si drawdown alto
            if abs(current_drawdown) > 0.10:
                risk_score -= 2
            elif abs(current_drawdown) > 0.05:
                risk_score -= 1
            
            # Penalizar si pérdida diaria alta
            if abs(daily_loss) > 0.03:
                risk_score -= 2
            elif abs(daily_loss) > 0.01:
                risk_score -= 1
            
            # Penalizar si volatilidad alta
            if volatility > 0.05:
                risk_score -= 1
            
            # Decisión basada en riesgo
            if risk_score <= -3:
                decision = Decision.STRONG_SELL  # Cerrar posiciones
                confidence = 0.9
                reasoning = "Riesgo CRÍTICO - Reducir exposición"
            elif risk_score == -2:
                decision = Decision.SELL
                confidence = 0.75
                reasoning = "Riesgo ALTO - Precaución"
            elif risk_score == -1:
                decision = Decision.HOLD
                confidence = 0.6
                reasoning = "Riesgo MODERADO - Mantener"
            else:
                decision = Decision.HOLD
                confidence = 0.5
                reasoning = "Riesgo BAJO - OK para operar"
            
            return AgentVote(
                agent_type=AgentType.RISK_MANAGER,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                metrics={
                    'risk_score': risk_score,
                    'drawdown': current_drawdown,
                    'var_95': var_95,
                    'volatility': volatility
                }
            )
        except Exception as e:
            logger.error(f"Error en Risk Manager Agent: {e}")
            return AgentVote(
                agent_type=AgentType.RISK_MANAGER,
                decision=Decision.HOLD,
                confidence=0.5,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    async def _portfolio_manager_agent_vote(
        self,
        portfolio_state: Dict,
        market_data: Dict
    ) -> AgentVote:
        """
        Agente Portfolio Manager: Optimiza portfolio
        Considera diversificación, correlación, rebalanceo
        """
        try:
            # Estado del portfolio
            positions = portfolio_state.get('positions', [])
            balance = portfolio_state.get('balance', 0)
            total_value = portfolio_state.get('total_value', balance)
            
            # Calcular exposición actual
            exposure = sum(p.get('value', 0) for p in positions) / total_value if total_value > 0 else 0
            
            # Decisión basada en exposición
            if exposure > 0.8:
                decision = Decision.SELL
                confidence = 0.8
                reasoning = f"Exposición alta ({exposure*100:.1f}%) - Reducir"
            elif exposure < 0.2:
                decision = Decision.BUY
                confidence = 0.7
                reasoning = f"Exposición baja ({exposure*100:.1f}%) - Aumentar"
            else:
                decision = Decision.HOLD
                confidence = 0.6
                reasoning = f"Exposición óptima ({exposure*100:.1f}%)"
            
            return AgentVote(
                agent_type=AgentType.PORTFOLIO_MANAGER,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                metrics={
                    'exposure': exposure,
                    'num_positions': len(positions),
                    'balance': balance
                }
            )
        except Exception as e:
            logger.error(f"Error en Portfolio Manager Agent: {e}")
            return AgentVote(
                agent_type=AgentType.PORTFOLIO_MANAGER,
                decision=Decision.HOLD,
                confidence=0.5,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    async def _regime_detector_agent_vote(self, market_data: Dict) -> AgentVote:
        """
        Agente Regime Detector: Detecta régimen de mercado
        TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE
        """
        try:
            # Indicadores de régimen
            trend = market_data.get('trend', 0)  # -1 a +1
            volatility = market_data.get('volatility', 0.02)
            volume_trend = market_data.get('volume_trend', 0)
            
            # Detectar régimen
            if abs(trend) < 0.2 and volatility < 0.02:
                regime = "RANGING"
                decision = Decision.HOLD
                confidence = 0.6
            elif trend > 0.3 and volatility < 0.03:
                regime = "TRENDING_UP"
                decision = Decision.BUY
                confidence = 0.8
            elif trend < -0.3 and volatility < 0.03:
                regime = "TRENDING_DOWN"
                decision = Decision.SELL
                confidence = 0.8
            elif volatility > 0.05:
                regime = "VOLATILE"
                decision = Decision.HOLD
                confidence = 0.7
            else:
                regime = "UNCERTAIN"
                decision = Decision.HOLD
                confidence = 0.4
            
            return AgentVote(
                agent_type=AgentType.REGIME_DETECTOR,
                decision=decision,
                confidence=confidence,
                reasoning=f"Régimen: {regime} (trend: {trend:.2f}, vol: {volatility:.3f})",
                metrics={
                    'regime': regime,
                    'trend': trend,
                    'volatility': volatility
                }
            )
        except Exception as e:
            logger.error(f"Error en Regime Detector Agent: {e}")
            return AgentVote(
                agent_type=AgentType.REGIME_DETECTOR,
                decision=Decision.HOLD,
                confidence=0.5,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    async def _sentiment_analyzer_agent_vote(
        self,
        sentiment_data: Dict,
        market_data: Dict
    ) -> AgentVote:
        """
        Agente Sentiment Analyzer: Analiza sentimiento
        Usa datos de Twitter, Reddit, News
        """
        try:
            # Sentimiento agregado
            sentiment = sentiment_data.get('aggregated_sentiment', 0)  # -1 a +1
            momentum = sentiment_data.get('momentum', 0)
            
            # Decisión basada en sentimiento
            if sentiment > 0.5:
                decision = Decision.STRONG_BUY
                confidence = min(sentiment, 0.9)
                reasoning = f"Sentimiento MUY POSITIVO ({sentiment:.2f})"
            elif sentiment > 0.2:
                decision = Decision.BUY
                confidence = min(sentiment + 0.3, 0.8)
                reasoning = f"Sentimiento POSITIVO ({sentiment:.2f})"
            elif sentiment < -0.5:
                decision = Decision.STRONG_SELL
                confidence = min(abs(sentiment), 0.9)
                reasoning = f"Sentimiento MUY NEGATIVO ({sentiment:.2f})"
            elif sentiment < -0.2:
                decision = Decision.SELL
                confidence = min(abs(sentiment) + 0.3, 0.8)
                reasoning = f"Sentimiento NEGATIVO ({sentiment:.2f})"
            else:
                decision = Decision.HOLD
                confidence = 0.5
                reasoning = f"Sentimiento NEUTRAL ({sentiment:.2f})"
            
            # Ajustar por momentum
            if momentum > 0.1 and decision in [Decision.BUY, Decision.STRONG_BUY]:
                confidence = min(confidence + 0.1, 0.95)
            elif momentum < -0.1 and decision in [Decision.SELL, Decision.STRONG_SELL]:
                confidence = min(confidence + 0.1, 0.95)
            
            return AgentVote(
                agent_type=AgentType.SENTIMENT_ANALYZER,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                metrics={
                    'sentiment': sentiment,
                    'momentum': momentum
                }
            )
        except Exception as e:
            logger.error(f"Error en Sentiment Analyzer Agent: {e}")
            return AgentVote(
                agent_type=AgentType.SENTIMENT_ANALYZER,
                decision=Decision.HOLD,
                confidence=0.5,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    async def _execution_optimizer_agent_vote(
        self,
        market_data: Dict,
        portfolio_state: Dict
    ) -> AgentVote:
        """
        Agente Execution Optimizer: Optimiza ejecución
        Considera liquidez, spread, timing
        """
        try:
            # Métricas de ejecución
            spread = market_data.get('spread', 0.001)
            liquidity = market_data.get('liquidity', 1.0)
            time_of_day = market_data.get('hour', 12)
            
            # Evaluar condiciones de ejecución
            execution_score = 0
            
            # Spread bajo es bueno
            if spread < 0.001:
                execution_score += 1
            elif spread > 0.005:
                execution_score -= 1
            
            # Alta liquidez es buena
            if liquidity > 0.8:
                execution_score += 1
            elif liquidity < 0.3:
                execution_score -= 1
            
            # Horarios óptimos (evitar aperturas/cierres)
            if 10 <= time_of_day <= 15:  # Horario óptimo
                execution_score += 1
            
            # Decisión
            if execution_score >= 2:
                decision = Decision.HOLD  # Condiciones óptimas para ejecutar
                confidence = 0.8
                reasoning = "Condiciones ÓPTIMAS para ejecutar"
            elif execution_score <= -2:
                decision = Decision.HOLD  # Esperar mejores condiciones
                confidence = 0.7
                reasoning = "Condiciones MALAS - Esperar"
            else:
                decision = Decision.HOLD
                confidence = 0.5
                reasoning = "Condiciones ACEPTABLES"
            
            return AgentVote(
                agent_type=AgentType.EXECUTION_OPTIMIZER,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning,
                metrics={
                    'execution_score': execution_score,
                    'spread': spread,
                    'liquidity': liquidity
                }
            )
        except Exception as e:
            logger.error(f"Error en Execution Optimizer Agent: {e}")
            return AgentVote(
                agent_type=AgentType.EXECUTION_OPTIMIZER,
                decision=Decision.HOLD,
                confidence=0.5,
                reasoning=f"Error: {str(e)}",
                metrics={}
            )
    
    def _aggregate_votes(self, votes: List[AgentVote]) -> Dict:
        """
        Agrega votos usando weighted voting
        Agentes con mejor performance tienen más peso
        """
        if not votes:
            return {'decision': Decision.HOLD, 'position_size': 0.0}
        
        # Calcular voto ponderado
        weighted_sum = 0
        total_weight = 0
        
        for vote in votes:
            # Peso del agente (performance histórica)
            agent_weight = self.agent_weights[vote.agent_type]
            
            # Peso por confianza
            confidence_weight = vote.confidence
            
            # Peso total
            weight = agent_weight * confidence_weight
            
            # Sumar voto ponderado
            weighted_sum += vote.decision.value * weight
            total_weight += weight
        
        # Decisión agregada
        if total_weight > 0:
            avg_vote = weighted_sum / total_weight
        else:
            avg_vote = 0
        
        # Convertir a Decision
        if avg_vote >= 1.5:
            decision = Decision.STRONG_BUY
        elif avg_vote >= 0.5:
            decision = Decision.BUY
        elif avg_vote <= -1.5:
            decision = Decision.STRONG_SELL
        elif avg_vote <= -0.5:
            decision = Decision.SELL
        else:
            decision = Decision.HOLD
        
        # Calcular position size basado en confianza
        position_size = min(abs(avg_vote) * 0.5, 1.0) if decision != Decision.HOLD else 0.0
        
        return {
            'decision': decision,
            'position_size': position_size,
            'weighted_vote': avg_vote
        }
    
    def _detect_conflicts(self, votes: List[AgentVote]) -> List[str]:
        """Detecta conflictos entre agentes"""
        conflicts = []
        
        # Agrupar por decisión
        buy_votes = [v for v in votes if v.decision.value > 0]
        sell_votes = [v for v in votes if v.decision.value < 0]
        
        # Conflicto si hay votos fuertes en ambas direcciones
        if buy_votes and sell_votes:
            strong_buy = any(v.decision == Decision.STRONG_BUY and v.confidence > 0.7 for v in buy_votes)
            strong_sell = any(v.decision == Decision.STRONG_SELL and v.confidence > 0.7 for v in sell_votes)
            
            if strong_buy and strong_sell:
                conflicts.append("CONFLICTO FUERTE: Señales opuestas con alta confianza")
        
        return conflicts
    
    def _resolve_conflicts(
        self,
        votes: List[AgentVote],
        conflicts: List[str],
        current_decision: Dict
    ) -> Dict:
        """Resuelve conflictos dando prioridad a Risk Manager"""
        
        # En caso de conflicto, dar prioridad al Risk Manager
        risk_vote = next((v for v in votes if v.agent_type == AgentType.RISK_MANAGER), None)
        
        if risk_vote and risk_vote.decision in [Decision.SELL, Decision.STRONG_SELL]:
            logger.warning("Conflicto resuelto: Prioridad a Risk Manager (SELL)")
            return {
                'decision': risk_vote.decision,
                'position_size': 0.0,
                'conflict_resolution': 'risk_priority'
            }
        
        return current_decision
    
    def _calculate_collective_confidence(
        self,
        votes: List[AgentVote],
        final_decision: Dict
    ) -> float:
        """Calcula confianza colectiva"""
        if not votes:
            return 0.0
        
        # Confianza promedio ponderada
        total_confidence = 0
        total_weight = 0
        
        for vote in votes:
            weight = self.agent_weights[vote.agent_type]
            total_confidence += vote.confidence * weight
            total_weight += weight
        
        return total_confidence / total_weight if total_weight > 0 else 0.0
    
    def _calculate_consensus(self, votes: List[AgentVote]) -> float:
        """Calcula nivel de consenso (0-1)"""
        if not votes:
            return 0.0
        
        # Contar votos por dirección
        buy_count = sum(1 for v in votes if v.decision.value > 0)
        sell_count = sum(1 for v in votes if v.decision.value < 0)
        hold_count = sum(1 for v in votes if v.decision.value == 0)
        
        total = len(votes)
        max_count = max(buy_count, sell_count, hold_count)
        
        return max_count / total
    
    def _save_to_history(self, result: Dict):
        """Guarda decisión en historial"""
        self.decision_history.append(result)
        
        # Limitar tamaño del historial
        if len(self.decision_history) > self.max_history:
            self.decision_history = self.decision_history[-self.max_history:]
    
    def update_agent_performance(self, agent_type: AgentType, was_correct: bool):
        """
        Actualiza performance de un agente
        Usado para adaptive weighting
        """
        perf = self.agent_performance[agent_type]
        perf['total_predictions'] += 1
        
        if was_correct:
            perf['correct_predictions'] += 1
        
        # Actualizar accuracy
        perf['accuracy'] = perf['correct_predictions'] / perf['total_predictions']
        
        # Ajustar peso del agente
        self._adjust_agent_weight(agent_type)
        
        logger.debug(f"{agent_type.value} accuracy: {perf['accuracy']:.2%}")
    
    def _adjust_agent_weight(self, agent_type: AgentType):
        """Ajusta peso del agente según performance"""
        accuracy = self.agent_performance[agent_type]['accuracy']
        
        # Aumentar peso si accuracy > 60%
        if accuracy > 0.6:
            self.agent_weights[agent_type] = min(self.agent_weights[agent_type] * 1.05, 0.4)
        # Reducir peso si accuracy < 45%
        elif accuracy < 0.45:
            self.agent_weights[agent_type] = max(self.agent_weights[agent_type] * 0.95, 0.05)
        
        # Normalizar pesos
        total = sum(self.agent_weights.values())
        for agent in AgentType:
            self.agent_weights[agent] /= total
    
    def get_agent_statistics(self) -> Dict:
        """Obtiene estadísticas de todos los agentes"""
        return {
            'weights': {agent.value: weight for agent, weight in self.agent_weights.items()},
            'performance': {
                agent.value: {
                    'accuracy': perf['accuracy'],
                    'total_predictions': perf['total_predictions']
                }
                for agent, perf in self.agent_performance.items()
            },
            'total_decisions': len(self.decision_history)
        }
