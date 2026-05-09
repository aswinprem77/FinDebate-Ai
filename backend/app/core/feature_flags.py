from pydantic import BaseModel


class FeatureFlags(BaseModel):
    auth_enabled: bool = True
    market_data_enabled: bool = True
    rate_limiter_enabled: bool = True
    debate_engine_enabled: bool = True
    judge_enabled: bool = False
    tier_renderer_enabled: bool = False


feature_flags = FeatureFlags()
