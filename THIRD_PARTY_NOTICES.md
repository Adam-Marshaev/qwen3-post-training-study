# Third-Party Notices

This repository documents experiments involving third-party model and
dataset resources. Its original source code, experiment configurations,
and research documentation are distinct from those upstream resources.

## Qwen3-0.6B-Base

- Provider: Qwen / Alibaba Cloud
- Model: Qwen/Qwen3-0.6B-Base
- Pinned model revision:
  57ca99e94acb83175495aa2c6b6b0cc498170924
- License: Apache License 2.0
- Model: https://huggingface.co/Qwen/Qwen3-0.6B-Base
- License text:
  https://huggingface.co/Qwen/Qwen3-0.6B-Base/blob/main/LICENSE

The model architecture and pretrained parameters are third-party work.

The repository does not include the original pretrained model weights
or trained LoRA checkpoint binaries in its tracked source files.

The project's own license does not replace the terms governing Qwen.
Anyone separately obtaining or redistributing the model or its
derivatives is responsible for complying with the applicable license,
including license and attribution requirements.

## GSM8K / Grade School Math

- Provider: OpenAI
- Dataset: GSM8K / grade-school-math
- Original source repository:
  https://github.com/openai/grade-school-math
- Dataset repository:
  https://huggingface.co/datasets/openai/gsm8k
- Dataset source revision recorded for this project:
  3101c7d5072418e28b9008a6636bde82a006892c
- License: MIT

The repository contains selected GSM8K training-partition
questions or prompt text in experimental review and preference-data
files. It does not publish the project's raw GSM8K dataset copy.

Selected experimental artifacts also contain model-generated
completions associated with GSM8K questions.

### Original GSM8K License Notice

The following copyright and license notice is reproduced from
the upstream OpenAI grade-school-math repository.

MIT License

Copyright (c) 2021 OpenAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Other Dependencies

The implementation uses PyTorch, Transformers, TRL, PEFT, and other
Python packages. Their respective upstream licenses continue to
govern those dependencies.

Refer to the Docker and Python project configuration for
environment details.

## Scope of This Notice

This file records third-party attribution. It does not grant
ownership of third-party model weights or datasets and does not
replace any applicable upstream license requirements.
