# Todo

## Features

- [X] Baker based on custom Shader
- [ ] Bake from source ( selected to active )
  - [ ] Cherry pick the list of sources for each target object
  - [ ] option to match source and target by name ?
  - [ ] option to load collection instead of objects -> updating objects in the collection change the setup ?
  - [ ] operator to match source and target by binding box
  - [ ] Bake from source with Cage
  - [ ] Cage Automatic Creation
  - [ ] Export automatic cage ?
  - [ ] Cage Shader
  - [ ] Cage distance painting
- [ ] add ability to load a scene as background before baker ( usefull for AO )
- [ ] add feature to apply background color per baker
- [ ] add bake from multires ? For Normal only
- [ ] Bake Skew Correction map
- [ ] Bake Decal ?
- [ ] Map Denoising ?
- [ ] Improve user control, feedback and reports
  - [ ] Add LOG in 3D viewport
  - [ ] Add LOG into a panel
  - [ ] Add LOG into text datablock ?
  - [ ] Add Operator to open .log file in text editor
  - [ ] Add Cancel, Pause, Resume Process -> does the executor need to be executed through a modal operators ?
  - [ ] Add progress bar : In 3D Viewport ? In the UI ? Both ?
- [ ] Every Adder ( Bake Group, Baker, Packer ) need to have a name collision prevention mechanism
- [ ] add check for target objects without UV -> Skip the mesh and raise a warning or block the execution of the bake ?
- [ ] add dynamic description to get and explain the registered tokens and transforms for filename
- [ ] Bake to Vertex Color
  - [ ] Being able to bake to vertex color -> add a "bake target" enum [["Image", "Color Attribute"]]
  - [ ] Adapt the planner to prevent creation of ownership task, accumulation map
  - [ ] may need specific accumulation or packer based on bmesh color manipulation
  - [ ] Adapt the display visualization to work in both cases
  - [ ] investigate how colorspace can be applied
- [ ] Preset System
- [ ] Bake external : Run another blender instance -> perform the bake -> import the result in current blender instance
- [ ] Bake network : Investigate the use of [Flamenco](https://flamenco.blender.org/) ?

## Baker

- [X] Diffuse
- [X] Ambient Occlusion
- [X] Albedo
- [X] Curvature
  - [ ] add option to have curvature using two Channel : [One for concave and one for convex](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZwnsY3ePkCHIu-GvNyl-Kr7-27NMkMm-btlTj02CAiINIVGu0Ovo-lp5V&s=10)
- [ ] Cavity
- [ ] Edge
- [ ] Normal
- [ ] Normal World Space
- [ ] Position
- [ ] Thickness
- [ ] ID
- [ ] Mask
- [ ] Opacity
- [ ] Roughness
- [ ] Metalness
- [ ] Glossiness
- [ ] Vector Displacement
- [ ] Vertex Color Channel
- [ ] Wireframe ?
- [ ] Custom Shader ? -> Is it different than albedo

## QOL

- [ ] force disable render visibility on all objects except the target objects before baking and recover after ?
- [ ] add an option to match render visibility to viewport visibility to prevent rendering hidden objects ?
