import torch
import torch.nn as nn
import json
import os

# Define constants exactly as required
INPUT_DIM = 64
OUTPUT_DIM = 128

class LatentBridge(nn.Module):
    def __init__(self):
        super(LatentBridge, self).__init__()
        # Linear projection without bias to simulate pure Procrustes matrix multiplication
        self.linear = nn.Linear(INPUT_DIM, OUTPUT_DIM, bias=False)
        # Initialize with orthogonal weights to simulate Procrustes alignment
        nn.init.orthogonal_(self.linear.weight)

    def forward(self, x):
        return self.linear(x)

def main():
    # Ensure we are running from the project root or adjust paths accordingly
    # For this PoC, we assume the script runs from the project root or ml/ dir.
    # Let's save outputs to the current working directory, which will be the project root
    # since we will run it as `python ml/export_bridge.py`.
    
    # 1. Instantiate the model and set to eval mode
    model = LatentBridge()
    model.eval()

    # 2. Generate random input tensor X simulating Agent A's latent vector
    # Create dummy input WITHOUT batch dimension
    x = torch.randn(INPUT_DIM)

    # 3. Compute the output Y
    with torch.no_grad():
        y = model(x)

    print(f"Input shape: {x.shape}")
    print(f"Output shape: {y.shape}")

    # 4. Export to ONNX without Dynamo
    onnx_filename = "bridge.onnx"
    torch.onnx.export(
        model,
        x,
        onnx_filename,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output']
    )
    print(f"Exported model to {onnx_filename}")

    # 5. Export input and output to input.json for EZKL
    data = {
        "input_data": [x.numpy().flatten().tolist()],
        "output_data": [y.numpy().flatten().tolist()]
    }
    
    input_json_filename = "input.json"
    with open(input_json_filename, "w") as f:
        json.dump(data, f)
    
    print(f"Exported input data to {input_json_filename}")

if __name__ == "__main__":
    main()
