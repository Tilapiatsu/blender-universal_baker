# Todo

## Features

- [X] Baker based on custom Shader
  - Node group is imported to, and all parameters are driven by the UI of the Baker
- [ ] Bake from source ( selected to active )
  - [ ] Cherry pick the list of sources for each target object
  - [ ] option to match source and target by name ?
  - [ ] option to load collection instead of objects -> updating objects in the collection change the setup ?
  - [ ] operator to match source and target by binding box
  - [ ] Bake from source with Cage
  - [ ] Cage Automatic Creation
  - [ ] Cage Shader
  - [ ] Cage distance painting
- [ ] add ability to load a scene as background before baker ( usefull for AO )
- [ ] add featuure to apply background color per baker
- [ ] add bake from multires
- [ ] Bake Skew Correction map
- [ ] Bake Decal ?
- [ ] Map Denoising ?
- [ ] Bake from and to Vertex Color
- [ ] Preset System

## Baker

- [X] Diffuse
- [X] Ambient Occlusion
- [ ] Albedo
- [X] Curvatue
  - [ ] add option to have curvature using two Channel : One for concave and one for convex
  <https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZwnsY3ePkCHIu-GvNyl-Kr7-27NMkMm-btlTj02CAiINIVGu0Ovo-lp5V&s=10>
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
