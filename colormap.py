import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from PIL import Image

# Mapa como string
map_string = """
S M . M . M . M . . . . . . . . M M . . . . . M . . . . . M 
* * . M . . . . . . M . . . . M . . . . . . . . . . M M . . 
. * . . . . . . . . . . M . . . M . . . . . . M . . . . . . 
. * M . . . . . . . . . . . . . . . . . . . . . . . . . . . 
. * . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
M * * * * * * . . . . . . . M . . . . . . . . . . . . M . . 
. . . . . M * . . M . . . . . . . . M . . . . M . . . . . . 
. . . . . . * . . . . . . . . . . . . . . . . . . M . . . . 
. . . . . . * . . . . . . . . . . M . . . . . . . . . . . . 
. M . M M . * . . . . . . . . . . . . . . . M . M M . . . . 
. . . . . . * * * * * . . . . . . . . . . . . . . . . . . . 
. . M . . M . M . . * * . . . . . . . . . M . M . M . . . . 
. . . . . . . . . . . * . . . . . . . . . M . . . . M . . . 
. . M . . . . . . . . * * . . . M . . . M . M . . . . . . . 
. . . . M . . . . . . . * * . . . . . M . . . . M M M M . . 
. . . . . . . . M . . M M * * G . M . . . . . . . . . . . . 
. . . M . . . . . . . . . . . . . . . . . . . . . M . . . . 
. . . . . . . . . . . . . . . . . . . . . . . . M . . . M . 
. . . . . . M . M . . . M M . . . . . . . . . . . . . . . . 
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
. . . . . . . . . . . . . . . . . . . . . . M . . . . . . . 
. . . . . . . . M . . . . . . . . . . . . . . . . . . . . . 
. . . . . . M . . M . . . . . . . . . . . . . . . . . . . . 
. . . . . . M . . . . . . . . . . . . . . M . . . . . . . . 
. . . . . . . . M . . . M . . . . . . . . M . . . . . . . . 
. . . . . . . . . . . . . M . . . . . . . . . . M . . . . . 
. . . . . . . . . . . . . . . . . . . . . . M . . . M . M . 
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
. . . M . . . . M . . . . . . . . M . . . . . . . . M . . . 
. . . . . . . . . . . . . M . . . . . . . . . . . . . . . . 
"""

# Etapa 1: Conversão da string para matriz numérica
lines = map_string.strip().splitlines()
matrix = [line.strip().split() for line in lines]
height = len(matrix)
width = len(matrix[0])
data = np.zeros((height, width))

mapping = {
    '.': 0,  # livre
    'M': 1,  # obstáculo
    '*': 2,  # caminho
    'S': 3,  # início
    'G': 4   # objetivo
}

for i in range(height):
    for j in range(width):
        data[i, j] = mapping.get(matrix[i][j], 0)

# Etapa 2: Abrir imagem e casar resoluções
bg_img = Image.open("random_country.jpg")
bg_array = np.asarray(bg_img)
img_height, img_width = bg_array.shape[0], bg_array.shape[1]

# Etapa 3: Fazer upscale do mapa para casar com a imagem
scale_y = img_height // height
scale_x = img_width // width
data_upscaled = np.kron(data, np.ones((scale_y, scale_x)))
data_upscaled = data_upscaled[:img_height, :img_width]

# Etapa 4: Colormap personalizado
cmap = ListedColormap([
    (1, 1, 1, 0),       # 0 - livre (transparente)
    (0.5, 0.5, 0.5, 0.8), # 1 - obstáculo
    (1, 0.84, 0, 0.99),  # 2 - caminho
    (0, 1, 0, 0.9),     # 3 - início
    (1, 0, 0, 0.9),     # 4 - objetivo
])

# Etapa 5: Plotagem
plt.figure(figsize=(8, 8))
plt.imshow(bg_array, extent=[0, img_width, 0, img_height], filterrad=0.1, filternorm=True, origin='lower')
plt.imshow(data_upscaled, cmap=cmap, origin='upper')
plt.axis('off')
plt.tight_layout()
plt.savefig("mapa_gerado.jpg", dpi=600)
plt.show()
