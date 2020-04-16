import argparse
import os
import shutil

import imageio
import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate
from PIL import Image, ImageDraw


np.random.seed(42)

m = 1.0  # kg
l = 1.0  # m
mu = 0.5  # kg m^2 / s
g = 9.81  # m / s^2

integration_start = 0.0  # s
integration_stop = 10.0  # s
integration_step = 0.1

image_size = 16
mass_offset = 1
border_offset = int(50 / 10.0)



def control_fn(t):
    return np.pi / 8



# Explicit first-order ODES of motion. y[0] is phi, y[1] is phiDot. Callable u(t) is the control input.
def motion_odes(y, t):
    phi = y[0]
    phi_dot = y[1]
    phi_ddot = (-mu * phi_dot + m * g * l * np.sin(phi) + control_fn(t)) / (m * l ** 2)
    return phi_dot, phi_ddot



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output_directory', help = 'The name of the output directory.')
    parser.add_argument('-f', '--force', action = 'store_true', help = f'Overwrite output directory directory if it exists.')
    args = parser.parse_args()
    out_dir = args.output_directory

    if os.path.exists(out_dir):
        if args.force:
            shutil.rmtree(out_dir)
        else:
            raise Exception('Output directory %s exists!' % out_dir)
    os.makedirs(out_dir)

    y0 = (0, 0)
    t = np.arange(integration_start, integration_stop, step = integration_step)
    sol = scipy.integrate.odeint(motion_odes, y0, t)
    phis = sol[:, 0]
    phi_dots = sol[:, 1]
    print(phis)
    print(phi_dots)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(t, phis, label = r'$\varphi(t)$')
    ax.plot(t, phi_dots, label = r'$\dot{\varphi}(t)$')
    ax.legend()
    ax.set_xlabel('t')
    fig.show()

    with imageio.get_writer(f'{out_dir}/pendulum.gif', mode = 'I', duration = integration_step) as gif_writer:
        for t, phi in zip(t, phis):
            # Calculate the x/y coordinates using basic trigonometry.
            x = l * np.sin(phi)
            y = -l * np.cos(phi)
            # Scale the length of the stick to use more space of the screen.
            x *= (image_size / 2 - border_offset) / l
            y *= (image_size / 2 - border_offset) / l
            # Move the pendulum base to the center of the screen.
            x += image_size / 2
            y += image_size / 2
            # Clip the values to integers as screens are so natural...
            x = int(x)
            y = int(y)

            image = Image.new('1', (image_size, image_size), color = 1)
            draw = ImageDraw.Draw(image)
            draw.ellipse(((x - mass_offset, y - mass_offset), (x + mass_offset, y + mass_offset)), fill = 0)
            image_path = '%s/pendulum-%06.3f.bmp' % (out_dir, t)
            image.save(image_path, format = 'BMP')
            gif_writer.append_data(imageio.imread(image_path))
