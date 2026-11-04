# Training issues
1. deepspeed_qwen_72b and deepspeed_qwen_7b failure:  No such file or directory "/opt/rocm/bin/rocminfo" <br> 
   Issue fixed by PR "[ROCm] Fix subprocess error" https://github.com/deepspeedai/DeepSpeed/pull/6587 <br>
2. deepspeed_qwen_72b and deepspeed_qwen_7b failure: Error "Input should be a valid integer" <br>
   Issue triaged and pointed to PR "Fix: Cast prefetch_bucket_size to integer for deepspeed >= 0.15" <br>
   https://github.com/huggingface/transformers/pull/33402 <br>
3. deepspeed_megatron_llama2 models failure: RuntimeError No HIP GPUs are available" <br>
   Issue fixed by PR "Revert hipblaslt" https://github.com/ROCm/apex/pull/141 <br>
4. DeepSpeed: Upstream changes in apply_rotary_pos_emb.cu to support threads_per_head < 64 <br>
   Issue fixed by PR "Support threads_per_head < 64 for wavefront size of 64" <br>
   https://github.com/deepspeedai/DeepSpeed/pull/6622 <br>
5. Fambench moe failure: RuntimeError Expected all tensors to be on the same device, but found at least two devices,
   cuda:0 and cpu!" <br>
   Issue fixed by PR "transformer_moe_layer: Fix Runtime error" https://github.com/pnunna93/fairseq/pull/1 <br>

# Inference issues
1. bert_inference_ph3 failure: IndexError: tuple index out of range <br>
   Issue fixed by PR "Fix torch cuda device to consider CUDA_VISIBLE_DEVICES" https://github.com/ROCm/pytorch/pull/1650 <br>
2. ort_huggingface_gpt2_fp32: Observing hip out of memory for batch size 64 with DLM workload <br>
   Issue fixed by internal PR "For mi250, if precision is fp32 then fix batch size to 16, default batch size is 22. <br>
   For mi300, if precision is fp32 then fix batch size to 32, default batch size to 64." <br>
   
