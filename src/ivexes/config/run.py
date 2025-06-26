from agents import (
    Model,
    ModelProvider,
    ModelSettings,
    OpenAIChatCompletionsModel,
    RunConfig,
)
from openai import AsyncOpenAI
from ivexes.config.settings import settings
import ivexes.config.log as log
import pprint


def get_config() -> RunConfig:
    logger = log.get(__name__)

    client = AsyncOpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)

    class CustomModelProvider(ModelProvider):
        def get_model(self, model_name: str | None) -> Model:
            return OpenAIChatCompletionsModel(
                model=model_name or settings.model, openai_client=client
            )

    run_config: RunConfig = RunConfig(
        model=settings.model,
        model_provider=CustomModelProvider(),
        model_settings=ModelSettings(temperature=settings.temperature),
    )

    logger.info(
        f'Runnning with url={settings.llm_base_url} and api_key={settings.llm_api_key[:10]}...'
    )
    logger.debug(f'run_config=\n{pprint.pformat(run_config)}')

    return run_config
