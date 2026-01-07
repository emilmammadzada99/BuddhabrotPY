import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

# =====================
# SETTINGS
# =====================
width, height = 1920, 1080
num_samples = 2_000_000
max_iter = 2000

# =====================
# NUMBA KERNEL
# =====================
@njit(parallel=True, fastmath=True)
def buddhabrot_numba(R, G, B, cr, ci, width, height, max_iter):
    n = cr.shape[0]

    for k in prange(n):
        zr = 0.0
        zi = 0.0

        cre = cr[k]
        cim = ci[k]

        # Cardioid test (skip points inside the main cardioid)
        q = (cre - 0.25)**2 + cim**2
        if q * (q + (cre - 0.25)) < 0.25 * cim**2:
            continue

        # Orbit buffer
        orbr = np.empty(max_iter, dtype=np.float64)
        orbi = np.empty(max_iter, dtype=np.float64)
        count = 0

        for i in range(max_iter):
            zr2 = zr*zr - zi*zi + cre
            zi  = 2*zr*zi + cim
            zr  = zr2

            orbr[count] = zr
            orbi[count] = zi
            count += 1

            # Escape condition
            if zr*zr + zi*zi > 4.0:
                if 80 < i < 1400:
                    for j in range(count):
                        x = int((orbr[j] + 2.0) / 3.0 * width)
                        y = int((orbi[j] + 1.2) / 2.4 * height)

                        if 0 <= x < width and 0 <= y < height:
                            if i < 200:
                                B[y, x] += 1
                                B[height-y-1, x] += 1
                            elif i < 600:
                                G[y, x] += 1
                                G[height-y-1, x] += 1
                            else:
                                R[y, x] += 1
                                R[height-y-1, x] += 1
                break

# =====================
# EXECUTION
# =====================
R = np.zeros((height, width), dtype=np.float64)
G = np.zeros((height, width), dtype=np.float64)
B = np.zeros((height, width), dtype=np.float64)

cr = np.random.uniform(-2.0, 1.0, num_samples)
ci = np.random.uniform(0.0, 1.2, num_samples)  # symmetry

buddhabrot_numba(R, G, B, cr, ci, width, height, max_iter)

# =====================
# COLOR NORMALIZATION (NO GLOW)
# =====================
img = np.stack([R, G, B], axis=-1)

img = np.log1p(img)      # dynamic range compression only
img /= img.max()
img = img ** 0.85        # mild gamma (does not blur details)

# =====================
# DISPLAY
# =====================
# plt.figure(figsize=(15, 10), dpi=150)
plt.figure(figsize=(19.2, 10.8), dpi=100)
plt.imshow(img, origin="lower")
plt.axis("off")
plt.savefig(
    "buddhabrot_1920x1080.png",
    dpi=100,
    bbox_inches="tight",
    pad_inches=0
)
plt.show()
