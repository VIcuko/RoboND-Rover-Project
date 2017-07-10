import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select

#Alternative color_thresh function
def color_thresh2(img, filter_type="ground"):
    options = {
        "ground": ground_filter(img),
        "noground" : rest_filter(img),
        "rock" : rock_filter(img)
    }
    return options[filter_type]

def ground_filter(img, rgb_thresh=(160,160,160)):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    color_select[above_thresh] = 1
    return color_select

def rest_filter(img, rgb_thresh=(160,160,160)):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] < rgb_thresh[0]) \
                & (img[:,:,1] < rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
    color_select[above_thresh] = 1
    return color_select

def rock_filter(img, rgb_top=(255,255,110),rgb_bottom=(160,160,0)):
    color_select = np.zeros_like(img[:,:,0])
    in_thresh = (img[:,:,0] < rgb_top[0]) \
                & (img[:,:,0] > rgb_bottom[0]) \
                & (img[:,:,1] < rgb_top[1]) \
                & (img[:,:,1] > rgb_bottom[1]) \
                & (img[:,:,2] < rgb_top[2]) \
                & (img[:,:,2] > rgb_bottom[2])
    color_select[in_thresh] = 1
    return color_select   

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    image = Rover.img
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
                  [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset], 
                  [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
                  ])
   
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    coloured_ground = color_thresh(image, rgb_thresh=(160, 160, 160))
    coloured_notground = color_thresh2(image,"noground")
    coloured_rock = color_thresh2(image,"rock")

    # 2) Apply perspective transform
    coloured_ground_t = perspect_transform(coloured_ground, source, destination)
    coloured_notground_t = perspect_transform(coloured_notground, source, destination)
    coloured_rock_t = perspect_transform(coloured_rock, source, destination)
    
    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:,:,0] = coloured_notground_t * 255
    Rover.vision_image[:,:,1] = coloured_rock_t * 255
    Rover.vision_image[:,:,2] = coloured_ground_t * 255

    # 5) Convert map image pixel values to rover-centric coords
    x_pixel, y_pixel = rover_coords(coloured_ground_t)
    x_pixel_nground, y_pixel_nground = rover_coords(coloured_notground_t)
    x_pixel_rock, y_pixel_rock = rover_coords(coloured_rock_t)  
    
    # 6) Convert rover-centric pixel values to world coordinates
    yaw = Rover.yaw
    xpos = Rover.pos[0]
    ypos = Rover.pos[1]
    world_size = 200
    scale = 10
    
    x_pix_world, y_pix_world = pix_to_world(x_pixel, y_pixel, xpos, ypos, yaw, world_size, scale)
    x_pix_world_nground, y_pix_world_nground = pix_to_world(x_pixel_nground, y_pixel_nground, xpos, ypos, yaw, world_size, scale)
    x_pix_world_rock, y_pix_world_rock = pix_to_world(x_pixel_rock, y_pixel_rock, xpos, ypos, yaw, world_size, scale)
    
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
        
    Rover.worldmap[y_pix_world_nground, x_pix_world_nground,0] +=10
    Rover.worldmap[y_pix_world_rock, x_pix_world_rock,1] +=10
    Rover.worldmap[y_pix_world, x_pix_world, 2] += 10
    
    navigable = Rover.worldmap[:,:,2] > 0
    Rover.worldmap[navigable,0]=0   

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists, Rover.nav_angles = to_polar_coords(x_pixel, y_pixel)    
    
    return Rover