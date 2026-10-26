# Architecture decision — October 26, 2026

Selected under Rahul's instruction to find the strongest approach and proceed. This is a reasoned choice under constraints, not an absolute-optimum claim.

## Choice

Public Python forecast/evaluation pipeline; static SvelteKit web surface; private placement in a worker using BGE-small q8; the same WASM inference and placement core in the terminal. No personal API or hosted personal LLM. Precomputed public data loads before the optional model.

| Alternative | Consequence for this project |
| --- | --- |
| Hosted personal placement | Conflicts with the approved promise that personal sentences and answers stay on-device. |
| Full generative LLM in browser | Larger download and device requirements; unnecessary for embedding and five public-default questions. |
| Separate native Python and browser models | Same weights produced measurable vector drift in the probe; more contracts to debug. |
| Saved samples only | Useful explicit fallback; cannot support arbitrary personal idea placement. |
| Shared WASM embedding and exact local neighbors | Meets privacy, supports arbitrary sentences, and provides one measurement contract; selected. |

## Measured engineering evidence

Eight synthetic sentences authored for the probe, on an Apple M1 Mac with 8 GB RAM. Browser assets were served from localhost after download. Model-cache bytes include model/tokenizer/config files, exclude runtime assets. Times are descriptive small-sample results, not an SLA.

| Model | Cache MB (decimal) | Browser median ms | Browser maximum ms among 8 | Dimensions |
| --- | ---: | ---: | ---: | ---: |
| MiniLM L6 | 23.69 | 36.1 | 133.8 | 384 |
| BGE-small | 34.73 | 78.1 | 90.7 | 384 |
| BGE-base | 110.80 | 208.4 | 362.9 | 768 |

All three returned the expected nearest synthetic paraphrase in the native probe. That trivial check does not establish task quality. BGE-small balances transfer and inference cost with the original model card's general retrieval results; no claim that it is best on hackathon ideas follows from those benchmarks.

The important finding is runtime consistency. BGE-small native ONNX versus browser differed by up to about 0.0111 in vector components. Replacing the native reference with the shared WASM path reduced the measured maximum absolute component difference to **1.1920928955078125e-7**. Use a tolerance, not a promise of cross-device bit identity. Exact runtimes/tokenizer/weights/pooling are part of a run contract.

BGE uses CLS pooling, per the [original model card](https://huggingface.co/BAAI/bge-small-en-v1.5). Do not adopt a mean-pooling example from another wrapper without validating its effect. Pin the ONNX conversion revision and file hashes. [ONNX deployment docs](https://onnxruntime.ai/docs/tutorials/web/deploy.html) cover runtime assets; model bytes alone are not the complete browser download.

Raw measurements and asset hashes: [architecture-benchmark.json](architecture-benchmark.json). The scratch probe is not product code or a forecast run. No public corpus score or human labels were produced.

## Rendering and hosting

[SvelteKit's static adapter](https://svelte.dev/docs/kit/adapter-static) produces files the visitor can use without a server. [Render static sites](https://render.com/docs/static-sites) offer CDN delivery and [custom response headers](https://render.com/docs/static-site-headers), including a policy on worker responses. This is the selected optional host; no deployment or paid plan has been authorized by this research. Bandwidth/build quotas still apply. The local app remains recordable.

UMAP is display only. Private points use deterministic local interpolation of public layout neighbors. Neither a gap on the canvas nor a jump across it is a density metric; all percentile calculations use the original vectors. A clear limitation is preferable to a second, inconsistent layout/runtime path.

## Checks still required

- Task-specific semantic placement review, a real forecast with measured defaults, and phone testing.
- Actual worker progress, Cancel/Forget races, canary network inspection and production response headers.
- Historical data access and pre-event brief/weight provenance; frozen protocol before corpus access.
- Rahul's blind labels and judge agreement before any claimed backtest success.

These are acceptance gates. Architecture feasibility does not establish the product's scientific claim.
