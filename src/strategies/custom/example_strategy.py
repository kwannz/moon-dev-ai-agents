from src.strategies.base_strategy import BaseStrategy

class ExampleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("Lumix Example Strategy")
    
    def generate_signals(self) -> dict:
        return {
            'token': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',
            'signal': 0.85,        # 0-1 strength
            'direction': 'BUY',    # BUY, SELL, or NEUTRAL
            'metadata': {
                'reason': '🚀 Strategy signals buy!',
                'indicators': {
                    'rsi': 28,
                    'trend': 'bullish'
                }
            }
        }  