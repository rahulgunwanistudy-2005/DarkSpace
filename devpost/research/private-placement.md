# Private placement — technical planning evidence

Checked October 26, 2026. Proposed approach, not an approved stack or a passed feasibility test.

## Constraint

The approved PRD keeps personal ideas and answers on the user's device. The kit's optional personal-placement API and cloud-generated personal interview questions cannot be retained as remote services under that promise. Colab/Kaggle remain options for public forecast and evaluation work only.

## Documentation findings

- Transformers.js supports in-browser inference using ONNX Runtime, with WASM CPU execution and optional WebGPU. The main documentation identifies v3.8.1 as the stable npm release at lookup time.
- Its official browser tutorial uses a Web Worker to keep inference/model loading from blocking the main interface, and shows model-loading progress callbacks.
- The `Xenova/bge-small-en-v1.5` card identifies it as an ONNX conversion of BAAI's model and demonstrates 384-dimensional sentence embeddings. This is a candidate, not a model selection; pooling, instruction policy, quantization, exact revision, provenance, and quality must be verified before adopting it. It is smaller than the kit's recommended base variant, so a quality tradeoff must be evaluated rather than assumed harmless.

Sources:
- https://huggingface.co/docs/transformers.js/index
- https://huggingface.co/docs/transformers.js/v3.8.1/index
- https://huggingface.co/docs/transformers.js/tutorials/next
- https://huggingface.co/Xenova/bge-small-en-v1.5

## Proposed split for learner review

Python/uv prepares public forecasts, evaluation artifacts, and static bundles. A static TypeScript web app displays those artifacts immediately. Personal embedding/placement runs on-device in a worker when available. A first model download has real loading cost; labeled saved samples remain usable without it. No user text goes to a personal-placement server.

The personal-placement embedding contract must be identical for the exported forecast vectors, browser, and terminal runner; do not compare vectors from different models or mix pooling/quantization rules. Browser/engine parity, input privacy, cancellation, download cost, and supported-device behavior require an early feasibility slice before reliance on arbitrary personal placement. Keep the fallback explicit if feasibility fails.

The companion should launch a local runner that reads the profile and handles answers itself, rather than forwarding private text through a hosted agent. The user may later choose to share the exported hand-off for scoping; that is a separate disclosure they control. Exact companion mechanics remain a spec decision.

## Not yet established

No chosen frontend framework, embedding model revision, download-size budget, measured phone performance, engine/browser parity result, or frozen backtest protocol. No forecast or evaluation run has occurred. Firecrawl retrieval failed due to exhausted credits; official documentation was read through web browsing instead.
