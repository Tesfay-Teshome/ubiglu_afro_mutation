class ClothingDesigner {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentModel = null;
        this.materials = {};
        this.measurements = {};
        this.styleOptions = {};
        
        this.init();
        this.setupEventListeners();
    }

    init() {
        // Initialize Three.js scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xffffff);

        // Setup camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.z = 5;

        // Setup renderer
        const canvas = document.getElementById('designCanvas');
        this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
        this.renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Setup lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(0, 1, 1);
        this.scene.add(directionalLight);

        // Setup controls
        this.controls = new THREE.OrbitControls(this.camera, canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 3;
        this.controls.maxDistance = 10;

        // Start animation loop
        this.animate();

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize(), false);
    }

    setupEventListeners() {
        // Garment type selection
        document.getElementById('garmentType').addEventListener('change', (e) => {
            this.loadGarment(e.target.value);
        });

        // Color selection
        document.getElementById('primaryColor').addEventListener('input', (e) => {
            this.updateColor('primary', e.target.value);
        });

        document.getElementById('secondaryColor').addEventListener('input', (e) => {
            this.updateColor('secondary', e.target.value);
        });

        // Measurements
        const measurementInputs = document.querySelectorAll('.measurements-form input');
        measurementInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateMeasurements(e.target.id, e.target.value);
            });
        });

        // Style options
        document.querySelectorAll('.style-options input, .style-options select').forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateStyle(e.target.id, e.target.value);
            });
        });

        // Fabric selection
        document.querySelectorAll('.fabric-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.selectFabric(e.target.closest('.fabric-item'));
            });
        });

        // View controls
        document.getElementById('rotateLeft').addEventListener('click', () => this.rotateModel(-Math.PI / 4));
        document.getElementById('rotateRight').addEventListener('click', () => this.rotateModel(Math.PI / 4));
        document.getElementById('resetView').addEventListener('click', () => this.resetView());

        // Save and order buttons
        document.getElementById('saveDesign').addEventListener('click', () => this.saveDesign());
        document.getElementById('orderDesign').addEventListener('click', () => this.orderDesign());
    }

    loadGarment(type) {
        const loader = new THREE.GLTFLoader();
        const dracoLoader = new THREE.DRACOLoader();
        dracoLoader.setDecoderPath('/static/core/js/draco/');
        loader.setDRACOLoader(dracoLoader);

        // Show loading state
        document.querySelector('.viewer').classList.add('loading');

        // Load the appropriate 3D model
        loader.load(
            `/static/core/models/${type}.glb`,
            (gltf) => {
                if (this.currentModel) {
                    this.scene.remove(this.currentModel);
                }
                this.currentModel = gltf.scene;
                this.scene.add(this.currentModel);
                
                // Setup materials
                this.setupMaterials();
                
                // Reset view
                this.resetView();
                
                // Hide loading state
                document.querySelector('.viewer').classList.remove('loading');
            },
            (xhr) => {
                console.log((xhr.loaded / xhr.total * 100) + '% loaded');
            },
            (error) => {
                console.error('Error loading model:', error);
                document.querySelector('.viewer').classList.remove('loading');
            }
        );
    }

    setupMaterials() {
        if (!this.currentModel) return;

        this.currentModel.traverse((child) => {
            if (child.isMesh) {
                // Create new materials for different parts
                const material = new THREE.MeshStandardMaterial({
                    color: 0xffffff,
                    roughness: 0.5,
                    metalness: 0.1
                });
                child.material = material;
                this.materials[child.name] = material;
            }
        });
    }

    updateColor(type, color) {
        const materialName = type === 'primary' ? 'MainFabric' : 'Accent';
        if (this.materials[materialName]) {
            this.materials[materialName].color.setStyle(color);
        }
    }

    selectFabric(fabricElement) {
        // Remove previous selection
        document.querySelectorAll('.fabric-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Add selection to clicked fabric
        fabricElement.classList.add('selected');

        // Load and apply texture
        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(fabricElement.dataset.texture, (texture) => {
            texture.wrapS = THREE.RepeatWrapping;
            texture.wrapT = THREE.RepeatWrapping;
            
            if (this.materials.MainFabric) {
                this.materials.MainFabric.map = texture;
                this.materials.MainFabric.needsUpdate = true;
            }
        });
    }

    updateMeasurements(measurement, value) {
        this.measurements[measurement] = parseFloat(value);
        this.updateModelDimensions();
    }

    updateModelDimensions() {
        if (!this.currentModel) return;

        // Apply measurements to the model
        // This would need to be customized based on your specific model structure
        const scale = this.calculateScale();
        this.currentModel.scale.set(scale, scale, scale);
    }

    updateStyle(option, value) {
        this.styleOptions[option] = value;
        // Update model based on style options
        // This would need to be customized based on your specific requirements
    }

    rotateModel(angle) {
        if (this.currentModel) {
            gsap.to(this.currentModel.rotation, {
                y: this.currentModel.rotation.y + angle,
                duration: 0.5,
                ease: "power2.out"
            });
        }
    }

    resetView() {
        if (!this.currentModel) return;

        gsap.to(this.camera.position, {
            x: 0,
            y: 1,
            z: 5,
            duration: 1,
            ease: "power2.inOut"
        });

        gsap.to(this.currentModel.rotation, {
            x: 0,
            y: 0,
            z: 0,
            duration: 1,
            ease: "power2.inOut"
        });

        this.controls.reset();
    }

    onWindowResize() {
        const canvas = this.renderer.domElement;
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height, false);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    async saveDesign() {
        const modal = new bootstrap.Modal(document.getElementById('saveDesignModal'));
        modal.show();

        document.getElementById('confirmSave').addEventListener('click', async () => {
            const designData = {
                name: document.getElementById('designName').value,
                description: document.getElementById('designDescription').value,
                measurements: this.measurements,
                styleOptions: this.styleOptions,
                // Capture thumbnail
                thumbnail: this.renderer.domElement.toDataURL('image/png')
            };

            try {
                const response = await fetch('/api/designs/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(designData)
                });

                if (response.ok) {
                    modal.hide();
                    // Show success message
                    const toast = new bootstrap.Toast(document.getElementById('saveSuccessToast'));
                    toast.show();
                } else {
                    throw new Error('Failed to save design');
                }
            } catch (error) {
                console.error('Error saving design:', error);
                // Show error message
            }
        });
    }

    orderDesign() {
        // Implement order functionality
        window.location.href = '/checkout/';
    }
}

// Initialize the designer when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const designer = new ClothingDesigner();
    
    // Load initial garment
    designer.loadGarment('shirt');
});
