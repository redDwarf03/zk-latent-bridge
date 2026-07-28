# Latent Geometry & Math Framing

In decentralized AI (DeAI), varying agents often leverage different foundation models (e.g., DINOv2 vs I-JEPA). When an agent needs to communicate its internal representation (latent state) to another agent, a direct exchange is not always compatible due to differences in latent space geometry and dimensionality.

## Procrustes Alignment and CKA

To bridge two distinct latent spaces, we can align them. Given a source latent space $\mathcal{X}$ and a target latent space $\mathcal{Y}$, we seek a transformation matrix $W$ that minimizes the distance between the transformed source features and target features. This is often solved using Orthogonal Procrustes analysis. The alignment quality can be quantified using Centered Kernel Alignment (CKA), as demonstrated in the [latent-inspector](https://github.com/AbdelStark/latent-inspector) research.

In this PoC (**zk-latent-bridge**), we abstract the complex derivation of $W$ and focus on proving the application of this translation matrix. Agent A applies the translation matrix $W$ to its latent vector $X$ to produce the aligned vector $Y$ intended for Agent B.

## Mathematical Formulation

The mathematical operation for the ZK circuit is a simple linear projection (matrix multiplication) between two latent spaces:

$$ Y = X W $$

Where:
- $X$ is a row vector representing the latent state of Agent A (Source).
- $W$ is the translation matrix derived from Procrustes alignment.
- $Y$ is the translated latent state compatible with Agent B (Target).

## Dimensions

To avoid Out-Of-Memory (OOM) errors common in standard ZK systems with full-scale model dimensions (e.g., DINOv2's 1024-dim or I-JEPA's 1280-dim), this PoC uses fixed reduced dimensions for the matrix multiplication:

- **INPUT_DIM**: `64` (Shape of $X$: $1 \times 64$)
- **OUTPUT_DIM**: `128` (Shape of $Y$: $1 \times 128$)
- **Shape of $W$**: `64 \times 128`

The goal of the zk-SNARK circuit is to prove that Agent A computed $Y$ correctly using the known translation matrix $W$, without revealing its private source latent vector $X$.
