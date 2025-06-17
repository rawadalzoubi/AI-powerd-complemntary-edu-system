import os
import logging
import argparse
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langdetect import detect 
import requests


# تأكد من استيراد Optional

# Import HuggingFace specific classes
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch # تأكد من استيراد torch إذا كنت ستستخدم torch.dtype مباشرة
import aiohttp
import asyncio # Explicitly import for asyncio.run if not already via aiohttp
import replicate # Add this import at the top
import openai # Import the OpenAI library

logger = logging.getLogger(__name__)
if not logger.hasHandlers(): # تحقق مما إذا كان قد تم تكوين logger بالفعل
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

class BaseLLM(ABC):
    """Abstract base class for LLM answer generators."""

    @abstractmethod
    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        pass

class OllamaLLM(BaseLLM):
    """Generates answers using Ollama HTTP API."""
    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434", request_timeout: int = 120):
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.request_timeout = request_timeout
        logger.info(f"Initialized Ollama LLM with model: {model_name} at {self.base_url}")

    async def _generate(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            url = f"{self.base_url}/api/generate"
            logger.debug(f"Ollama request: POST {url} with payload {payload}")
            try:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.request_timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error ({response.status}): {error_text} for model {self.model_name}")
                        raise Exception(f"Ollama API error ({response.status}): {error_text}")

                    result = await response.json()
                    logger.debug(f"Ollama response: {result}")
                    generated_text = result.get('response')
                    if not generated_text:
                        logger.warning(f"Ollama model {self.model_name} returned an empty response for prompt: '{prompt[:100]}...'")
                        return ""
                    return generated_text.strip()
            except aiohttp.ClientConnectorError as e:
                logger.error(f"Ollama connection error: {e}. Is Ollama server running at {self.base_url}?")
                raise Exception(f"Ollama connection error: {e}")
            except asyncio.TimeoutError:
                logger.error(f"Ollama request timed out after {self.request_timeout}s for model {self.model_name}.")
                raise Exception(f"Ollama request timed out after {self.request_timeout}s.")
            except Exception as e:
                logger.error(f"An unexpected error occurred during Ollama generation: {e}", exc_info=True)
                raise

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and context."""
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])

        # --- بداية الأمر (Prompt) المحسّن ---
        prompt = f"""أنت مساعد دراسي أكاديمي وخبير، متخصص في تقديم شروحات وافية، مفصلة، ودقيقة. مهمتك هي تمكين الطالب من فهم المواد الدراسية بعمق من خلال تحليل سؤاله وتقديم إجابة شاملة بناءً على "السياق" المقدم فقط.

إذا كان السؤال يتطلب حلاً لمسألة أو فهم طريقة معينة:
1. اشرح المفاهيم الأساسية من "السياق" التي ترتبط بالسؤال.
2. وضّح الخطوات اللازمة للوصول إلى الحل، مستشهداً بالمعلومات من "السياق".
3. قدم إرشادات وتلميحات تساعد الطالب على التفكير والوصول إلى الحل بنفسه. تجنب إعطاء الإجابة النهائية مباشرة للمسائل التي تتطلب خطوات حل.

إذا كان السؤال يطلب شرحًا لمفهوم ما، فقدم شرحًا وافيًا، واضحًا، ومنهجيًا بالاعتماد الكلي على "السياق". احرص على تغطية جوانب المفهوم المختلفة المذكورة في السياق، ووضح أي مصطلحات أساسية، وقدم أمثلة من السياق إذا كانت متوفرة وتساعد على الفهم. يجب أن تكون إجابتك منظمة وسهلة المتابعة.

إذا كان "السياق" لا يحتوي على معلومات كافية للإجابة على السؤال، يجب أن تذكر بوضوح: "المعلومات المتوفرة في السياق لا تكفي للإجابة على هذا السؤال."
يجب أن تكون جميع إجاباتك وإرشاداتك مستندة بالكامل إلى "السياق" المقدم. لا تستخدم أي معلومات خارجية.

**معايير الإجابة الاحترافية والمفصلة:**
* **العمق والشمولية:** قدم إجابات تتجاوز السطحية، وتشرح الأسباب والمبادئ الأساسية المتعلقة بالسؤال بناءً على ما هو متوفر في "السياق".
* **الدقة اللغوية والعلمية:** استخدم لغة دقيقة ومصطلحات صحيحة كما وردت في "السياق".
* **التنظيم والوضوح:** قسم الإجابات الطويلة إلى فقرات أو نقاط لتسهيل القراءة والفهم.
* **التركيز على الطالب:** هدفك هو مساعدة الطالب على الفهم الحقيقي، وليس مجرد تقديم معلومات.

**تعليمات اللغة:** يرجى الرد **بنفس اللغة المستخدمة في "سؤال الطالب"**. إذا كان السؤال باللغة العربية، أجب باللغة العربية. إذا كان السؤال باللغة الإنجليزية، أجب باللغة الإنجليزية.

السياق:
{context_text}

سؤال الطالب: {question}

الشرح والإرشادات المفصلة:"""
        # --- نهاية الأمر (Prompt) المحسّن ---

        logger.info(f"Generating Ollama answer for question: \"{question[:100]}...\" with model {self.model_name}")
        try:
            return asyncio.run(self._generate(prompt))
        except Exception as e:
            logger.error(f"Error in Ollama generate_answer: {e}", exc_info=True)
            return "Sorry, I encountered an error while generating the answer with Ollama."

class HuggingFaceLLM(BaseLLM):
    """
    Generates answers using a local HuggingFace CausalLM or Seq2Seq model.
    Defaults to CausalLM behavior suitable for models like Mistral, Llama, GPT.
    """
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.1", device: Optional[str] = None, use_seq2seq: bool = False, torch_dtype: Optional[Any] = None, huggingface_api_key: Optional[str] = None):
        self.model_name = model_name
        self.use_seq2seq = use_seq2seq
        self.huggingface_api_key = huggingface_api_key
        
        # Auto-detect device if not provided
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"No device specified, automatically selected: {self.device}")

        self.torch_dtype_arg = {}
        if torch_dtype:
            if isinstance(torch_dtype, str) and torch_dtype.lower() == "auto": self.torch_dtype_arg = {"torch_dtype": "auto"}
            elif isinstance(torch_dtype, str) and hasattr(torch, torch_dtype.replace("torch.","")):
                self.torch_dtype_arg = {"torch_dtype": getattr(torch, torch_dtype.replace("torch.",""))}
            elif hasattr(torch, 'dtype') and isinstance(torch_dtype, torch.dtype):
                self.torch_dtype_arg = {"torch_dtype": torch_dtype}
            else:
                logger.warning(f"torch_dtype '{torch_dtype}' not recognized as valid. Loading with default dtype.")

        logger.info(
            f"Initializing HuggingFaceLLM: model='{model_name}', device='{self.device}', "
            f"use_seq2seq='{use_seq2seq}', dtype_args='{self.torch_dtype_arg}', "
            f"token_present='{bool(self.huggingface_api_key)}'"
        )

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=self.huggingface_api_key)
            
            # Prepare arguments for loading the model
            model_load_kwargs = self.torch_dtype_arg.copy()
            if self.huggingface_api_key:
                model_load_kwargs["token"] = self.huggingface_api_key
            
            # Use device_map='auto' for intelligent device placement.
            # This is more efficient than .to(device) for larger models.
            model_load_kwargs['device_map'] = 'auto'

            logger.info(f"Loading model with arguments: {model_load_kwargs}")

            if self.use_seq2seq:
                self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, **model_load_kwargs)
            else:
                self.model = AutoModelForCausalLM.from_pretrained(model_name, **model_load_kwargs)
            
            # The .to(self.device) call is no longer needed as device_map handles placement.
            self.model.eval()
            # We can log the final device of the model to confirm it's on the GPU
            logger.info(f"HuggingFace model {model_name} loaded successfully. Final device: {self.model.device}")
        except Exception as e:
            logger.error(f"Error initializing HuggingFace model {model_name}: {e}", exc_info=True)
            raise

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and context."""
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])

        # --- بداية الأمر (Prompt) المحسّن ---
        prompt = f"""أنت مساعد دراسي أكاديمي وخبير، متخصص في تقديم شروحات وافية، مفصلة، ودقيقة. مهمتك هي تمكين الطالب من فهم المواد الدراسية بعمق من خلال تحليل سؤاله وتقديم إجابة شاملة بناءً على "السياق" المقدم فقط.

إذا كان السؤال يتطلب حلاً لمسألة أو فهم طريقة معينة:
1. اشرح المفاهيم الأساسية من "السياق" التي ترتبط بالسؤال.
2. وضّح الخطوات اللازمة للوصول إلى الحل، مستشهداً بالمعلومات من "السياق".
3. قدم إرشادات وتلميحات تساعد الطالب على التفكير والوصول إلى الحل بنفسه. تجنب إعطاء الإجابة النهائية مباشرة للمسائل التي تتطلب خطوات حل.

إذا كان السؤال يطلب شرحًا لمفهوم ما، فقدم شرحًا وافيًا، واضحًا، ومنهجيًا بالاعتماد الكلي على "السياق". احرص على تغطية جوانب المفهوم المختلفة المذكورة في السياق، ووضح أي مصطلحات أساسية، وقدم أمثلة من السياق إذا كانت متوفرة وتساعد على الفهم. يجب أن تكون إجابتك منظمة وسهلة المتابعة.

إذا كان "السياق" لا يحتوي على معلومات كافية للإجابة على السؤال، يجب أن تذكر بوضوح: "المعلومات المتوفرة في السياق لا تكفي للإجابة على هذا السؤال."
يجب أن تكون جميع إجاباتك وإرشاداتك مستندة بالكامل إلى "السياق" المقدم. لا تستخدم أي معلومات خارجية.

**معايير الإجابة الاحترافية والمفصلة:**
* **العمق والشمولية:** قدم إجابات تتجاوز السطحية، وتشرح الأسباب والمبادئ الأساسية المتعلقة بالسؤال بناءً على ما هو متوفر في "السياق".
* **الدقة اللغوية والعلمية:** استخدم لغة دقيقة ومصطلحات صحيحة كما وردت في "السياق".
* **التنظيم والوضوح:** قسم الإجابات الطويلة إلى فقرات أو نقاط لتسهيل القراءة والفهم.
* **التركيز على الطالب:** هدفك هو مساعدة الطالب على الفهم الحقيقي، وليس مجرد تقديم معلومات.

**تعليمات اللغة:** يرجى الرد **بنفس اللغة المستخدمة في "سؤال الطالب"**. إذا كان السؤال باللغة العربية، أجب باللغة العربية. إذا كان السؤال باللغة الإنجليزية، أجب باللغة الإنجليزية.

السياق:
{context_text}

سؤال الطالب: {question}

الشرح والإرشادات المفصلة:"""
        # --- نهاية الأمر (Prompt) المحسّن ---

        logger.info(f"Generating HuggingFace answer for question: \"{question[:100]}...\" with model {self.model_name}")

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(self.device)
            input_ids_length = inputs.input_ids.shape[1]

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1 # إضافة مقترح لمعالجة التكرار
                )

            if not self.use_seq2seq:
                answer_tokens = outputs[0][input_ids_length:]
            else:
                answer_tokens = outputs[0]

            answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)

            logger.debug(f"Generated answer (raw): {answer}")
            return answer.strip()

        except Exception as e:
            logger.error(f"Error generating HuggingFace answer: {e}", exc_info=True)
            return "Sorry, I encountered an error while generating the answer with HuggingFace."

class ReplicateLLM(BaseLLM):
    """Generates answers using the Replicate API."""
    def __init__(self, replicate_model_identifier: str, replicate_api_token: str, request_timeout: int = 120):
        self.replicate_model_identifier = replicate_model_identifier
        self.replicate_api_token = replicate_api_token
        self.request_timeout = request_timeout

        if not self.replicate_api_token:
            raise ValueError("Replicate API token is required for ReplicateLLM.")
        if not self.replicate_model_identifier:
            raise ValueError("Replicate model identifier is required for ReplicateLLM.")

        # Set the Replicate API token as an environment variable if it's not already
        # The replicate library primarily uses the REPLICATE_API_TOKEN environment variable.
        if "REPLICATE_API_TOKEN" not in os.environ or os.environ["REPLICATE_API_TOKEN"] != self.replicate_api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.replicate_api_token
            logger.info("REPLICATE_API_TOKEN environment variable set from config.")

        logger.info(f"Initialized ReplicateLLM with model identifier: {self.replicate_model_identifier}")

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and context using Replicate."""
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])

        # Using the same detailed prompt structure as other LLMs
        prompt = f"""أنت مساعد دراسي أكاديمي وخبير، متخصص في تقديم شروحات وافية، مفصلة، ودقيقة. مهمتك هي تمكين الطالب من فهم المواد الدراسية بعمق من خلال تحليل سؤاله وتقديم إجابة شاملة بناءً على "السياق" المقدم فقط.

إذا كان السؤال يتطلب حلاً لمسألة أو فهم طريقة معينة:
1. اشرح المفاهيم الأساسية من "السياق" التي ترتبط بالسؤال.
2. وضّح الخطوات اللازمة للوصول إلى الحل، مستشهداً بالمعلومات من "السياق".
3. قدم إرشادات وتلميحات تساعد الطالب على التفكير والوصول إلى الحل بنفسه. تجنب إعطاء الإجابة النهائية مباشرة للمسائل التي تتطلب خطوات حل.

إذا كان السؤال يطلب شرحًا لمفهوم ما، فقدم شرحًا وافيًا، واضحًا، ومنهجيًا بالاعتماد الكلي على "السياق". احرص على تغطية جوانب المفهوم المختلفة المذكورة في السياق، ووضح أي مصطلحات أساسية، وقدم أمثلة من السياق إذا كانت متوفرة وتساعد على الفهم. يجب أن تكون إجابتك منظمة وسهلة المتابعة.

إذا كان "السياق" لا يحتوي على معلومات كافية للإجابة على السؤال، يجب أن تذكر بوضوح: "المعلومات المتوفرة في السياق لا تكفي للإجابة على هذا السؤال."
يجب أن تكون جميع إجاباتك وإرشاداتك مستندة بالكامل إلى "السياق" المقدم. لا تستخدم أي معلومات خارجية.

**معايير الإجابة الاحترافية والمفصلة:**
* **العمق والشمولية:** قدم إجابات تتجاوز السطحية، وتشرح الأسباب والمبادئ الأساسية المتعلقة بالسؤال بناءً على ما هو متوفر في "السياق".
* **الدقة اللغوية والعلمية:** استخدم لغة دقيقة ومصطلحات صحيحة كما وردت في "السياق".
* **التنظيم والوضوح:** قسم الإجابات الطويلة إلى فقرات أو نقاط لتسهيل القراءة والفهم.
* **التركيز على الطالب:** هدفك هو مساعدة الطالب على الفهم الحقيقي، وليس مجرد تقديم معلومات.

**تعليمات اللغة:** يرجى الرد **بنفس اللغة المستخدمة في "سؤال الطالب"**. إذا كان السؤال باللغة العربية، أجب باللغة العربية. إذا كان السؤال باللغة الإنجليزية، أجب باللغة الإنجليزية.

السياق:
{context_text}

سؤال الطالب: {question}

الشرح والإرشادات المفصلة:"""

        logger.info(f"Generating Replicate answer for question: \"{question[:100]}...\" with model {self.replicate_model_identifier}")
        
        input_data = {
            "prompt": prompt,
            # Add other model-specific parameters here if needed, e.g., max_length, temperature.
            # These depend on the specific Replicate model you are using.
            # For Llama-3 based models, "prompt" is standard.
            # Example:
            # "max_new_tokens": 500,
            # "temperature": 0.75,
        }

        try:
            logger.debug(f"Calling replicate.run with model: {self.replicate_model_identifier} and input keys: {list(input_data.keys())}")
            # The output from replicate.run is typically an iterator for streaming, 
            # or a list of strings if the model generates multiple outputs.
            # For most text generation models, it will stream parts of the answer.
            output_parts = []
            for item in replicate.run(self.replicate_model_identifier, input=input_data):
                output_parts.append(str(item))
            
            generated_text = "".join(output_parts)

            if not generated_text:
                logger.warning(f"Replicate model {self.replicate_model_identifier} returned an empty response for prompt: \'{prompt[:100]}...\'")
                return "Sorry, the model returned an empty answer."
            return generated_text.strip()

        except replicate.exceptions.ReplicateError as e:
            logger.error(f"Replicate API error for model {self.replicate_model_identifier}: {e}", exc_info=True)
            return f"Sorry, I encountered an API error with Replicate: {e}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during Replicate generation for model {self.replicate_model_identifier}: {e}", exc_info=True)
            return "Sorry, I encountered an unexpected error while generating the answer with Replicate."

class OpenAILLM(BaseLLM):
    """Generates answers using the OpenAI API."""
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo", request_timeout: int = 120):
        if not api_key:
            raise ValueError("OpenAI API key is required for OpenAILLM.")
        self.model_name = model_name
        self.request_timeout = request_timeout
        self.client = openai.OpenAI(api_key=api_key, timeout=request_timeout)
        logger.info(f"Initialized OpenAI LLM with model: {model_name}")

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and context using OpenAI API."""
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])

        prompt = f"""أنت مساعد دراسي أكاديمي وخبير، متخصص في تقديم شروحات وافية، مفصلة، ودقيقة. مهمتك هي تمكين الطالب من فهم المواد الدراسية بعمق من خلال تحليل سؤاله وتقديم إجابة شاملة بناءً على "السياق" المقدم فقط.

إذا كان السؤال يتطلب حلاً لمسألة أو فهم طريقة معينة:
1. اشرح المفاهيم الأساسية من "السياق" التي ترتبط بالسؤال.
2. وضّح الخطوات اللازمة للوصول إلى الحل، مستشهداً بالمعلومات من "السياق".
3. قدم إرشادات وتلميحات تساعد الطالب على التفكير والوصول إلى الحل بنفسه. تجنب إعطاء الإجابة النهائية مباشرة للمسائل التي تتطلب خطوات حل.

إذا كان السؤال يطلب شرحًا لمفهوم ما، فقدم شرحًا وافيًا، واضحًا، ومنهجيًا بالاعتماد الكلي على "السياق". احرص على تغطية جوانب المفهوم المختلفة المذكورة في السياق، ووضح أي مصطلحات أساسية، وقدم أمثلة من السياق إذا كانت متوفرة وتساعد على الفهم. يجب أن تكون إجابتك منظمة وسهلة المتابعة.

إذا كان "السياق" لا يحتوي على معلومات كافية للإجابة على السؤال، يجب أن تذكر بوضوح: "المعلومات المتوفرة في السياق لا تكفي للإجابة على هذا السؤال."
يجب أن تكون جميع إجاباتك وإرشاداتك مستندة بالكامل إلى "السياق" المقدم. لا تستخدم أي معلومات خارجية.

**معايير الإجابة الاحترافية والمفصلة:**
* **العمق والشمولية:** قدم إجابات تتجاوز السطحية، وتشرح الأسباب والمبادئ الأساسية المتعلقة بالسؤال بناءً على ما هو متوفر في "السياق".
* **الدقة اللغوية والعلمية:** استخدم لغة دقيقة ومصطلحات صحيحة كما وردت في "السياق".
* **التنظيم والوضوح:** قسم الإجابات الطويلة إلى فقرات أو نقاط لتسهيل القراءة والفهم.
* **التركيز على الطالب:** هدفك هو مساعدة الطالب على الفهم الحقيقي، وليس مجرد تقديم معلومات.

**تعليمات اللغة:** يرجى الرد **بنفس اللغة المستخدمة في "سؤال الطالب"**. إذا كان السؤال باللغة العربية، أجب باللغة العربية. إذا كان السؤال باللغة الإنجليزية، أجب باللغة الإنجليزية.

السياق:
{context_text}

سؤال الطالب: {question}

الشرح والإرشادات المفصلة:"""

        logger.info(f"Generating OpenAI answer for question: \"{question[:100]}...\" with model {self.model_name}")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful and expert academic study assistant."}, # System message
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512,
                timeout=self.request_timeout
            )
            answer = response.choices[0].message.content.strip()
            if not answer:
                logger.warning(f"OpenAI model {self.model_name} returned an empty response for prompt: '{prompt[:100]}...'")
                return "Sorry, the model returned an empty answer."
            return answer
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}", exc_info=True)
            return f"Sorry, I encountered a connection error with OpenAI: {e}"
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {e}", exc_info=True)
            return f"Sorry, the OpenAI API rate limit was exceeded: {e}"
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API status error ({e.status_code}): {e.response}", exc_info=True)
            return f"Sorry, I encountered an API error with OpenAI: {e.status_code} - {e.response}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI generation: {e}", exc_info=True)
            return "Sorry, I encountered an unexpected error while generating the answer with OpenAI."

class DeepSeekLLM(BaseLLM):
    """Generates answers using the DeepSeek API."""
    def __init__(self, api_key: str, model_name: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1", request_timeout: int = 120):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.request_timeout = request_timeout
        if not self.api_key:
            raise ValueError("DeepSeek API key is required for DeepSeekLLM.")
        logger.info(f"Initialized DeepSeek LLM with model: {model_name} at {self.base_url}")

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])
        prompt = f"""أنت مساعد دراسي أكاديمي وخبير، متخصص في تقديم شروحات وافية، مفصلة، ودقيقة. مهمتك هي تمكين الطالب من فهم المواد الدراسية بعمق من خلال تحليل سؤاله وتقديم إجابة شاملة بناءً على \"السياق\" المقدم فقط.\n\nالسياق:\n{context_text}\n\nسؤال الطالب: {question}\n\nالشرح والإرشادات المفصلة:"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=self.request_timeout)
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            return answer
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}", exc_info=True)
            return f"Sorry, I encountered an error with DeepSeek: {e}"

class OpenRouterLLM(BaseLLM):
    """Generates answers using the OpenRouter API."""
    def __init__(self, api_key: str, model_name: str = "openrouter-chat", base_url: str = "https://openrouter.ai/api/v1", request_timeout: int = 120):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.request_timeout = request_timeout
        if not self.api_key:
            raise ValueError("OpenRouter API key is required for OpenRouterLLM.")
        logger.info(f"Initialized OpenRouter LLM with model: {model_name} at {self.base_url}")

    def generate_answer(self, question: str, context: List[Dict[str, Any]]) -> str:
        context_text = "\n\n".join(chunk['text'] for chunk in context if 'text' in chunk and chunk['text'])
        prompt = f"""أنت مرشد أكاديمي وموجه للطلاب، ولست آلة لحل المسائل.

مهمتك الأساسية: هي تمكين الطالب من حل واجبه بنفسه. لا تقدم الحل النهائي أبدًا (مثل نتيجة رقمية نهائية أو الكود المكتمل). بدلاً من ذلك، قم بتفكيك المشكلة، اشرح المفاهيم اللازمة من "السياق"، وقدم الخطوات التي يجب على الطالب اتباعها للوصول إلى الحل.

قواعد الإجابة الإرشادية:
1.  ركز على "كيفية" الحل وليس "ما هو" الحل:
    * صحيح: "لحل هذه المسألة، عليك استخدام نظرية فيثاغورث a^2 + b^2 = c^2 وتطبيقها على الأرقام المعطاة."
    * خاطئ: "الإجابة النهائية هي 5."

2.  قدم مثالاً موجهاً: عند تقديم مثال توضيحي، قم بحل الخطوات الأولى منه واترك الخطوة النهائية للطالب ليكملها.
    * مثال جيد: "لدينا 3^2 + 4^2 = c^2`، مما يعني `9 + 16 = c^2`، إذن `25 = c^2. الآن، ما هي الخطوة التالية لإيجاد قيمة `c`؟"

3.  الهيكلة والتنسيق: نظّم إجابتك في شكل خطوات واضحة باستخدام القوائم الرقمية. اجعل المصطلحات الهامة بالخط العريض لتسهيل القراءة.

4.  اللغة: أجب بنفس لغة "سؤال الطالب". عند الإجابة بالعربية، استخدم لغة عربية فصيحة ومصطلحات دقيقة وتجنب إقحام كلمات من لغات أخرى.

5.  الالتزام بالسياق: يجب أن تكون جميع إجاباتك وإرشاداتك مستندة بالكامل إلى "السياق" المقدم. إذا كانت المعلومات غير متوفرة، اذكر ذلك بوضوح.

---
السياق:
{context_text}

---
سؤال الطالب: {question}

---
خطوات الحل المقترحة (بدون الإجابة النهائية):"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://openrouter.ai",
            "X-Title": "AI Homework Helper",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2048,
            "temperature": 0.9
        }
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data, timeout=self.request_timeout)
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            return answer
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}", exc_info=True)
            return f"Sorry, I encountered an error with OpenRouter: {e}"

def create_llm_answer(llm_type: str = "ollama", **kwargs) -> BaseLLM:
    """
    Factory to create an LLM answer generator.
    """
    logger.info(f"Attempting to create LLM of type: {llm_type} with kwargs: {kwargs}")
    if llm_type == "ollama":
        # Specific kwargs for OllamaLLM
        ollama_kwargs = {
            "model_name": kwargs.get("model_name", "mistral"), # Default from OllamaLLM
            "base_url": kwargs.get("ollama_base_url", "http://localhost:11434"), # Default from OllamaLLM
            "request_timeout": kwargs.get("request_timeout", 120) # Default from OllamaLLM
        }
        return OllamaLLM(**ollama_kwargs)
    elif llm_type == "huggingface":
        # Specific kwargs for HuggingFaceLLM
        hf_kwargs = {
            "model_name": kwargs.get("model_name", "mistralai/Mistral-7B-Instruct-v0.1"), # Default from HuggingFaceLLM
            "device": kwargs.get("huggingface_device"),
            "use_seq2seq": kwargs.get("use_seq2seq", False), # Default from HuggingFaceLLM
            "torch_dtype": kwargs.get("huggingface_llm_torch_dtype_str"), # Name implies it's a string or None
            "huggingface_api_key": kwargs.get("huggingface_api_key")
        }
        return HuggingFaceLLM(**hf_kwargs)
    elif llm_type == "replicate":
        # Specific kwargs for ReplicateLLM
        replicate_kwargs = {
            "replicate_model_identifier": kwargs.get("replicate_model_identifier"),
            "replicate_api_token": kwargs.get("replicate_api_token"),
            "request_timeout": kwargs.get("request_timeout", 120) # Consistent default
        }
        if not replicate_kwargs["replicate_model_identifier"] or not replicate_kwargs["replicate_api_token"]:
            missing_keys = [k for k, v in replicate_kwargs.items() if not v and k != "request_timeout"] # Don't list timeout as missing if default
            logger.error(f"Missing required arguments for ReplicateLLM: {missing_keys}")
            raise ValueError(f"Missing required arguments for ReplicateLLM: {missing_keys}")
        return ReplicateLLM(**replicate_kwargs)
    elif llm_type == "openai": # Add new condition for OpenAI
        openai_kwargs = {
            "api_key": kwargs.get("openai_api_key"),
            "model_name": kwargs.get("model_name", "gpt-3.5-turbo"), # Default from OpenAILLM
            "request_timeout": kwargs.get("request_timeout", 120)
        }
        if not openai_kwargs["api_key"]:
            logger.error("OpenAI API key is required but was not provided.")
            raise ValueError("OpenAI API key is required for OpenAILLM.")
        return OpenAILLM(**openai_kwargs)
    elif llm_type == "deepseek":
        deepseek_kwargs = {
            "api_key": kwargs.get("deepseek_api_key"),
            "model_name": kwargs.get("model_name", "deepseek-chat"),
            "base_url": kwargs.get("deepseek_base_url", "https://api.deepseek.com/v1"),
            "request_timeout": kwargs.get("request_timeout", 120)
        }
        if not deepseek_kwargs["api_key"]:
            logger.error("DeepSeek API key is required but was not provided.")
            raise ValueError("DeepSeek API key is required for DeepSeekLLM.")
        return DeepSeekLLM(**deepseek_kwargs)
    elif llm_type == "openrouter":
        openrouter_kwargs = {
            "api_key": kwargs.get("openrouter_api_key"),
            "model_name": kwargs.get("model_name", "openrouter-chat"),
            "base_url": kwargs.get("openrouter_base_url", "https://openrouter.ai/api/v1"),
            "request_timeout": kwargs.get("request_timeout", 120)
        }
        if not openrouter_kwargs["api_key"]:
            logger.error("OpenRouter API key is required but was not provided.")
            raise ValueError("OpenRouter API key is required for OpenRouterLLM.")
        return OpenRouterLLM(**openrouter_kwargs)
    else:
        logger.error(f"Unknown LLM type requested: {llm_type}")
        raise ValueError(f"Unknown LLM type: {llm_type}. Supported types: ['ollama', 'huggingface', 'replicate', 'openai']") # Update supported types

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM runner: choose Ollama or HuggingFace.")
    parser.add_argument("--llm", choices=["ollama", "huggingface", "replicate", "openai"], default="huggingface", help="LLM type to use.")
    parser.add_argument("--model", type=str, help="Model name for the chosen LLM type.")
    parser.add_argument("--base_url", type=str, default="http://localhost:11434", help="Ollama server URL.")
    parser.add_argument("--question", type=str, default="What is the capital of France?", help="Question to ask.")
    parser.add_argument("--context", type=str, nargs="*", default=["France is a country in Europe. Paris is its capital."], help="Context chunks.")
    parser.add_argument("--device", type=str, default=None, help="Device for HuggingFace model (e.g., 'cuda', 'cpu').")
    parser.add_argument("--use_seq2seq", action="store_true", help="For HuggingFace, load model as Seq2Seq.")
    parser.add_argument("--torch_dtype", type=str, default=None, help="PyTorch dtype for HuggingFace model (e.g., 'bfloat16', 'auto').")
    parser.add_argument("--hf_token", type=str, default=os.getenv("HUGGINGFACE_API_KEY"), help="Hugging Face API Key (reads from HUGGINGFACE_API_KEY env var if not set).")
    parser.add_argument("--openai_api_key", type=str, default=os.getenv("OPENAI_API_KEY"), help="OpenAI API Key (reads from OPENAI_API_KEY env var if not set).")
    
    args = parser.parse_args()
    llm_instance: BaseLLM
    actual_torch_dtype = None
    if args.torch_dtype:
        if args.torch_dtype.lower() == "auto":
            actual_torch_dtype = "auto"
        elif hasattr(torch, args.torch_dtype.replace("torch.","")):
            actual_torch_dtype = getattr(torch, args.torch_dtype.replace("torch.",""))
        else:
            logger.warning(f"Torch dtype '{args.torch_dtype}' not recognized. Using model's default.")

    llm_params = {}
    if args.llm == "ollama":
        ollama_model_name = args.model or "mistral"
        llm_params = {"model_name": ollama_model_name, "base_url": args.base_url}
    elif args.llm == "openai":
        openai_model_name = args.model or "gpt-3.5-turbo"
        llm_params = {
            "model_name": openai_model_name,
            "openai_api_key": args.openai_api_key
        }
    else: # huggingface or replicate
        hf_model_name = args.model or "mistralai/Mistral-7B-Instruct-v0.1" # يمكنك تغيير هذا الافتراضي إذا أردت
        llm_params = {
            "model_name": hf_model_name,
            "device": args.device,
            "use_seq2seq": args.use_seq2seq,
            "torch_dtype": actual_torch_dtype,
            "huggingface_api_key": args.hf_token
        }

    llm_instance = create_llm_answer(args.llm, **llm_params)
    ctx = [{"text": txt} for txt in args.context]
    logger.info(f"Question: {args.question}")
    answer = llm_instance.generate_answer(args.question, ctx)
    print("\n--- Generated Answer ---")
    print(answer)