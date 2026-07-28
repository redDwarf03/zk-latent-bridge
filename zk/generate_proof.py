import os
import json
import subprocess
import ezkl

def run_cmd(args):
    print(f"Running: {' '.join(args)}")
    env = os.environ.copy()
    if "HOME" not in env and "USERPROFILE" in env:
        env["HOME"] = env["USERPROFILE"]
    subprocess.run(args, check=True, env=env)

def main():
    # Derive the absolute path of the repository root dynamically
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(base_dir, 'bridge.onnx')
    data_path = os.path.join(base_dir, 'input.json')
    settings_path = os.path.join(base_dir, 'settings.json')
    compiled_model_path = os.path.join(base_dir, 'network.compiled')
    srs_path = os.path.join(base_dir, 'kzg.srs')
    vk_path = os.path.join(base_dir, 'vk.key')
    pk_path = os.path.join(base_dir, 'pk.key')
    proof_path = os.path.join(base_dir, 'proof.json')
    abi_path = os.path.join(base_dir, 'LatentBridgeVerifier.abi')

    contracts_src = os.path.join(base_dir, 'contracts', 'src')
    os.makedirs(contracts_src, exist_ok=True)
    sol_code_path = os.path.join(contracts_src, 'LatentBridgeVerifier.sol')
    calldata_path = os.path.join(base_dir, 'calldata.json')
    ezkl_cli = 'ezkl'

    print("Generating settings...")
    ezkl.gen_settings(model_path, settings_path)
    
    # Enforce strict privacy directly in the settings JSON
    print("Enforcing strict privacy in settings.json...")
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    if "run_args" in settings:
        if "variables" in settings["run_args"]:
            settings["run_args"]["variables"] = []
        # Ensure scale is set
        settings["run_args"]["scale"] = 12
        # Set visibility for strict privacy
        settings["run_args"]["input_visibility"] = "Private"
        settings["run_args"]["param_visibility"] = "Fixed"
        settings["run_args"]["output_visibility"] = "Public"
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)

    # Calibrate settings with fallback
    print("Calibrating settings (optional but good)...")
    try:
        run_cmd([ezkl_cli, "calibrate-settings", "-M", model_path, "-O", settings_path, "-D", data_path, "--target", "resources"])
    except subprocess.CalledProcessError as e:
        print(f"Warning: Calibration failed or not available, proceeding with default settings. Error: {e}")

    print("Compiling circuit...")
    run_cmd([ezkl_cli, "compile-circuit", "-M", model_path, "-S", settings_path, "--compiled-circuit", compiled_model_path])

    print("Getting SRS...")
    run_cmd([ezkl_cli, "get-srs", "-S", settings_path, "--srs-path", srs_path])

    print("Generating witness...")
    witness_path = os.path.join(base_dir, 'witness.json')
    run_cmd([ezkl_cli, "gen-witness", "-D", data_path, "-M", compiled_model_path, "-O", witness_path])

    print("Mocking circuit...")
    run_cmd([ezkl_cli, "mock", "-M", compiled_model_path, "-W", witness_path])

    print("Running setup...")
    run_cmd([ezkl_cli, "setup", "-M", compiled_model_path, "-W", witness_path, "--srs-path", srs_path, "--vk-path", vk_path, "--pk-path", pk_path])

    print("Proving...")
    run_cmd([ezkl_cli, "prove", "-M", compiled_model_path, "-W", witness_path, "--pk-path", pk_path, "--proof-path", proof_path, "--srs-path", srs_path])

    print("Creating EVM verifier...")
    run_cmd([ezkl_cli, "create-evm-verifier", "--vk-path", vk_path, "-S", settings_path, "--srs-path", srs_path, "--sol-code-path", sol_code_path, "--abi-path", abi_path])
    
    print("Encoding EVM calldata...")
    run_cmd([ezkl_cli, "encode-evm-calldata", "--proof-path", proof_path, "--calldata-path", calldata_path])

    # Patch LatentBridgeVerifier.sol to avoid Stack Too Deep in Foundry
    print("Patching LatentBridgeVerifier.sol for memory-safe assembly...")
    with open(sol_code_path, 'r') as f:
        sol_content = f.read()
    sol_content = sol_content.replace('assembly {', 'assembly ("memory-safe") {')
    with open(sol_code_path, 'w') as f:
        f.write(sol_content)

    print("Done! ZK proof and EVM verifier generated successfully.")

if __name__ == "__main__":
    main()
