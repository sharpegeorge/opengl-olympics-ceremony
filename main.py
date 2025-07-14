import pygame

# import the scene class
from cubeMap import FlattenCubeMap
from scene import Scene

from lightSource import LightSource

from blender import load_obj_file, load_vertices_from_obj

from BaseModel import DrawModelFromMesh

from shaders import *

from ShadowMapping import *

from sphereModel import Sphere

from skyBox import *

from environmentMapping import *

class ExeterScene(Scene):
    def __init__(self):
        Scene.__init__(self)

        self.environment = EnvironmentMappingTexture(width=400, height=400)

        self.light = LightSource(self, position=[0., 7.1, 0.])
        self.shaders = 'phong'

        # Animated balloon variables
        self.balloonHeight = 0
        self.animationRunning = False
        self.goingUp = True

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)

        # Load the static scene
        meshes = load_obj_file('models/scene5.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
        )

        # Load fake light sources to give different shader
        meshes = load_obj_file('models/lightvertices.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=MaxBrightnessShader(), name='scene') for mesh in meshes]
        )

        # Load water independently to give environment shaders
        meshes = load_obj_file('models/water.obj')
        self.add_models_list(
            [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=EnvironmentShader(map=self.environment), name='scene') for mesh in meshes]
        )
        
        # Load all meshes of the balloon and add each part separately
        balloon_meshes = load_obj_file('models/balloon.obj')
        self.balloon_parts = []
        for i, mesh in enumerate(balloon_meshes):
            balloon_part = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0, -1, 0]), scaleMatrix([0.5, 0.5, 0.5])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name=f'balloon')
            self.balloon_parts.append(balloon_part)
            self.add_model(balloon_part)

        # Draw skybox
        self.skybox = SkyBox(scene=self)

    def move_balloon_up(self):
        self.balloonHeight += 1
        for part in self.balloon_parts:
            part.M = np.matmul(part.M, translationMatrix([0, 0.2, 0]))  # move balloon parts up by 1 unit

        # Move the light source up by 1 unit
        self.light.position[1] += 0.1

    def move_balloon_down(self):
        self.balloonHeight -= 1
        for part in self.balloon_parts:
            part.M = np.matmul(part.M, translationMatrix([0, -0.2, 0]))  # move balloon parts down by 1 unit

        # Move the light source down by 1 unit
        self.light.position[1] -= 0.1

    def update(self):
        # Used in game loop to animate balloon when activated
        if self.animationRunning:
            maxBalloonHeight = 40
            minBalloonHeight = 0

            # Checking if the balloon should change directions
            if self.balloonHeight == maxBalloonHeight:
                self.goingUp = False
            elif self.balloonHeight == minBalloonHeight:
                self.goingUp = True

            # Either move balloon up or down
            if self.goingUp:
                self.move_balloon_up()
            else:
                self.move_balloon_down()

    def draw_shadow_map(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def draw_reflections(self):
        self.skybox.draw()
        for model in self.models:
            model.draw()

    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not framebuffer:
            self.camera.update()

        self.skybox.draw()
        self.shadows.render(self)

        if not framebuffer:
            self.environment.update(self)
            self.show_shadow_map.draw()

        for model in self.models:
            model.draw()

        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''

        if event.key == pygame.K_f:
            self.animationRunning = False

        if event.key == pygame.K_s:
            self.animationRunning = True


if __name__ == '__main__':
    # initialises the scene object
    scene = ExeterScene()

    # starts drawing the scene
    scene.run()
