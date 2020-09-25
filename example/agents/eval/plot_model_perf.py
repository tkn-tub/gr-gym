import matplotlib.pyplot as plt
import numpy as np
from tensorflow import keras

model_path = './rl/gnugym_rl_wifi/'
model = keras.models.load_model(model_path)

r = np.arange(0, 1.0, 0.01) #np.random.rand(200)

xv = []
yv = []

for ii in range(r.shape[0]):
    x = r[ii]
    y = np.argmax(model.predict(x))

    xv.append(r[ii])
    yv.append(y)

plt.scatter(xv, yv)
plt.grid()

plt.title(model_path)
plt.show()
