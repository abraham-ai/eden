from __future__ import print_function
import argparse
import math
import numpy as np
from io import BytesIO
import PIL.Image
from IPython.display import clear_output, Image, display, HTML
import scipy.misc
from noise import pnoise2, snoise2


def process_arguments(args):
    parser = argparse.ArgumentParser(description='modifier')
    parser.add_argument('--img_in', action='store', required=True, type=str)
    parser.add_argument('--img_out', action='store', required=True, type=str)
    parser.add_argument('--img_blend', action='store', required=True, type=str)
    parser.add_argument('--amt_blend', action='store', required=True, type=float)
    params = vars(parser.parse_args(args))
    return params


def showarray(a, fmt='jpeg'):
    a = np.uint8(np.clip(a, 0, 1)*255)
    f = BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue()))


def get_image(path, w, h):
    img = scipy.misc.imread(path, mode='RGB')
    img = scipy.misc.imresize(img, (h, w))
    return img


def view_canvas(canvas, h, w, numframes, filename=None):
    img = make_image_grid(w, h) if filename is None else get_image(filename, w, h)
    showarray(img/255.)
    for i in range(numframes):
        img = modify_canvas(img, canvas)
        showarray(img/255.)

        
def make_image_grid(w, h, spacing=15, thickness=3):
    img = np.zeros((h, w, 3))
    for off in range(thickness):
        img[:,range(off, w, spacing),0] = 255
        img[range(off, h, spacing),:,0] = 255
    img[range(-8+int(h/2),8+int(h/2)),range(-8+int(w/2),8+int(w/2)),:] = [0,255,0]
    img[range(8+int(h/2),-8+int(h/2),-1),range(-8+int(w/2),8+int(w/2)),:] = [0,255,0]
    return img


def lerp_mod(mod1, mod2, r):
    mod_avg = {}
    for k in mod1:
        try:
            mod_avg[k] = (1.0 - r) * mod1[k] + r * mod2[k]
        except:
            mod_avg[k] = tuple([ (1.0 - r) * m1_ + r * m2_ for m1_, m2_ in zip(mod1[k], mod2[k]) ])
    return mod_avg


def map_image(img, idx):  # should it be mod by h-1, w-1?
    h, w = img.shape[0:2]
    idx = np.array(idx).reshape((h*w, 2))
    idx_mod = np.mod(idx,[h,w])  
    idx_turn = np.mod(np.floor_divide(idx,[h,w]),2)
    idx = np.multiply(idx_mod,1-idx_turn)+np.multiply([h,w]-idx_mod,idx_turn)
    idx = np.clip(idx, [0,0], [h-1,w-1])
    idx = np.array(idx).astype('float32')
    idx_tl = np.floor(np.copy(idx).astype('float32')).astype('int32')
    idx_br = np.ceil(np.copy(idx).astype('float32')).astype('int32')
    idx_tr = np.copy(idx_tl).astype('int32')
    idx_bl = np.copy(idx_br).astype('int32')
    idx_tr[:,1] = idx_br[:,1]
    idx_bl[:,1] = idx_tl[:,1]
    diff = np.subtract(idx, idx_tl)
    dy, dx = diff[:, 0].reshape((h*w, 1)), diff[:, 1].reshape((h*w, 1))
    img_tl = img[idx_tl[:,0], idx_tl[:,1], :]
    img_tr = img[idx_tr[:,0], idx_tr[:,1], :]
    img_bl = img[idx_bl[:,0], idx_bl[:,1], :]
    img_br = img[idx_br[:,0], idx_br[:,1], :]
    img_t = np.add(np.multiply(np.subtract(1.0, dx), img_tl), np.multiply(dx, img_tr))
    img_b = np.add(np.multiply(np.subtract(1.0, dx), img_bl), np.multiply(dx, img_br))
    img_f = np.add(np.multiply(np.subtract(1.0, dy), img_t), np.multiply(dy, img_b))
    img_f = img_f.reshape((h, w, 3))
    return img_f


def modify_canvas(img, mods, masks=None):
    h, w = img.shape[0:2]
    mods = mods if isinstance(mods, list) else [mods]
    masks = masks / np.sum(masks, axis=2)[:, :, np.newaxis] if masks is not None else np.ones((h, w, len(mods)))

    # make default grid
    grid = np.mgrid[0:w, 0:h].T
    grid[:,:,0], grid[:,:,1] = grid[:,:,1], grid[:,:,0].copy()
    mod_idxs = np.copy([[grid]*3]*len(mods))
    
    # calculate all th index transformations
    for idxm, mod in enumerate(mods):
        shift, stretch = mod['shift'], mod['stretch']
        zoom, expand = mod['zoom'], mod['expand']
        rot_const, rot_ang, rot_dst = mod['rot_const'], mod['rot_ang'], mod['rot_dst']
        spiral_margin, spiral_periods = mod['spiral_margin'], mod['spiral_periods']
        noise_rate, noise_margin = mod['noise_rate'], mod['noise_margin']
        cy, cx = h * mod['center'][0], w * mod['center'][1]

        # check in advance on what operations so as to save time
        to_shift = (shift[0] != 0.0 or shift[1] != 0.0 or stretch[0] != 1.0 or stretch[1] != 1.0)
        to_zoom = (zoom != 1.0 or expand != 0.0)
        to_spiral = (spiral_margin > 0)
        to_rotate = (rot_const != 0.0 or rot_ang != 0.0 or rot_dst != 0.0)
        to_noise = (noise_margin[0] != 0.0 or noise_margin[0] != 0.0)

        # create initial grid for transformations
        if to_shift or to_zoom or to_spiral or to_rotate:
            grid = np.mgrid[0:w, 0:h].T
            dfc = grid-[cx, cy]

        # zooming, spirals/rotations
        if to_zoom or to_spiral or to_rotate:
            dfc2 = np.power(dfc, 2)
            dst = np.power(np.sum(dfc2, axis=2), 0.5)
            ang = np.arctan2(dfc[:,:,1], dfc[:,:,0])
            dst2, ang2 = dst, ang

        # xy stretch/compress/shift
        if to_shift:
            stretch_mul = 1.0 / stretch[0], 1.0 / stretch[1]
            sy = cy - h * shift[0] + dfc[:,:,1] * stretch_mul[0]
            sx = cx - w * shift[1] + dfc[:,:,0] * stretch_mul[1]
            idx2 = np.dstack([sy, sx])
            mod_idxs[idxm][0] = idx2

        # expand/contract, plain zoom + radial
        if to_zoom:
            dst2 = np.add(np.multiply(1.0/zoom, dst), -expand).clip(min=0)

        # more complex dist multiply
        if to_spiral:
            dst2 = np.multiply(dst2, 1.0 + spiral_margin * np.sin(spiral_periods * ang))

        # rotation
        if to_rotate:
            ang2 = np.add(ang, rot_const + rot_ang * ang + rot_dst * dst)

        # re-map according to dst2 and ang2
        if to_zoom or to_spiral or to_rotate:
            idx_a = ang2[grid[:,:,1], grid[:,:,0]]
            idx_d = dst2[grid[:,:,1], grid[:,:,0]]
            idx_sin = cy + np.multiply(idx_d, np.sin(idx_a))
            idx_cos = cx + np.multiply(idx_d, np.cos(idx_a))
            idx2 = np.dstack((np.array(idx_sin), np.array(idx_cos)))
            mod_idxs[idxm][1] = idx2

        # perlin noise, very inefficient because of the double for loop
        if to_noise:
            offyy, offyx, offxy, offxx = 400, 200, 300, 100
            nyy, nyx, nxy, nxx = noise_rate[1], noise_rate[1], noise_rate[0], noise_rate[0]
            midy, marginy = 0.5*(-noise_margin[0]+noise_margin[0]), 0.5*(noise_margin[0]--noise_margin[0])
            midx, marginx = 0.5*(-noise_margin[1]+noise_margin[1]), 0.5*(noise_margin[1]--noise_margin[1])
            idx2 = [[(y+midy+marginy*snoise2(offyy+nyy*y/h, offyx+nyx*x/w, 3), 
                      x+midx+marginx*snoise2(offxy+nxy*y/h, offxx+nxx*x/w, 3)) 
                    for x in range(w)] for y in range(h)]
            mod_idxs[idxm][2] = idx2

    # average shift-indexes and transform the image
    for i in range(len(mod_idxs[0])):
        idxs = [np.multiply(mod_idxs[m][i], np.expand_dims(masks[:,:,m], 2)) for m in range(len(mods))]
        idx2 = np.sum(idxs, axis=0)
        img = map_image(img, idx2)

    return img


def modimg_old(mod, img_in, img_out, img_blend=None, amt_blend=None):
    img0 = scipy.misc.imread(img_in)
    img1 = modify_canvas(img0, mod)
    # blending
    if (amt_blend is not None and amt_blend > 0):
        img2 = scipy.misc.imread(img_blend)
        img3 = (1.0 - amt_blend) * img1 + amt_blend * img2
    else:
        img3 = img1
    
    scipy.misc.imsave(img_out, img3)

    
def warp_image(mod, img_in, img_blend=None, amt_blend=None):
    img_out = modify_canvas(img_in, mod)
    if (img_blend is not None and amt_blend is not None and amt_blend > 0):
        img_out = (1.0 - amt_blend) * img_out + amt_blend * img_blend
    return img_out


def main(img_in, img_blend, img_out, amt_blend):
    mod = {'center':(0.5, 0.5),
      'shift':(0,0), 'stretch':(1.0, 1.0), 
      'zoom':1.016, 'expand':0, 
      'rot_const':0.003, 'rot_ang':0, 'rot_dst':0,
      'spiral_margin':0, 'spiral_periods':0,
      'noise_rate':(0, 0), 'noise_margin':(0, 0)}
    img_in = scipy.misc.imread(img_in)
    img_blend = scipy.misc.imread(img_blend)
    img = warp_image(img_in, img_blend, amt_blend, mod)
    scipy.misc.imsave(img, img_out)


if __name__ == '__main__':
    params = process_arguments(sys.argv[1:])
    img_in = params['img_in']
    img_out = params['img_out']
    img_blend = params['img_blend']
    amt_blend = float(params['amt_blend'])    
    main(img_in, img_blend, img_out, amt)
