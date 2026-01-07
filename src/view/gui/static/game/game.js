const config = {
    type: Phaser.AUTO,
    width: window.innerWidth,
    height: window.innerHeight,
    backgroundColor: '#1a1a1a',
    parent: 'game-container',
    pixelArt: true,
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

const TILE_WIDTH = 64;  
const TILE_HEIGHT = 32; 

function preload() {
    this.load.image('floor', 'assets/floor.png');
    this.load.image('wall', 'assets/wall.png');
    this.load.image('trap', 'assets/trap.png');
    this.load.image('start', 'assets/start.png');
    this.load.image('exit', 'assets/exit.png');
}

function create() {
    const scene = this;
    
    // Récupération des données du donjon (sans chemin)
    fetch('/api/dungeon')
        .then(res => res.json())
        .then(data => {
            buildIsoGrid(scene, data);
        })
        .catch(err => console.error("Erreur chargement donjon:", err));
        
    // Centrage de la caméra
    this.cameras.main.centerOn(0, 0);
    this.cursors = this.input.keyboard.createCursorKeys();
}

function buildIsoGrid(scene, data) {
    const grid = data.grid;
    const originX = scene.sys.game.config.width / 2;
    const originY = 100;

    grid.forEach(row => {
        row.forEach(cell => {
            // Conversion Cartésien -> Isométrique
            const isoX = (cell.x - cell.y) * (TILE_WIDTH / 2) + originX;
            const isoY = (cell.x + cell.y) * (TILE_HEIGHT / 2) + originY;

            // 1. Sol (toujours présent)
            let floor = scene.add.image(isoX, isoY, 'floor');
            floor.setOrigin(0.5, 1.0);
            floor.setDepth(isoY);

            // 2. Entités par dessus le sol
            if (cell.type === 'WALL') {
                let wall = scene.add.image(isoX, isoY, 'wall');
                wall.setOrigin(0.5, 1.0);
                wall.setDepth(isoY + 1); // +1 pour passer devant le sol
            } 
            else if (cell.type === 'TRAP') {
                let trap = scene.add.image(isoX, isoY, 'trap');
                trap.setOrigin(0.5, 1.0);
                trap.setDepth(isoY + 1);
            }
            else if (cell.type === 'START') {
                let start = scene.add.image(isoX, isoY, 'start');
                start.setOrigin(0.5, 1.0);
                start.setDepth(isoY + 1);
            }
            else if (cell.type === 'EXIT') {
                let exit = scene.add.image(isoX, isoY, 'exit');
                exit.setOrigin(0.5, 1.0);
                // La sortie est souvent plate, donc même profondeur que le sol ou légèrement plus
                exit.setDepth(isoY + 1);
            }
        });
    });
}

function update() {
    const speed = 8;
    if (this.cursors.left.isDown) this.cameras.main.scrollX -= speed;
    if (this.cursors.right.isDown) this.cameras.main.scrollX += speed;
    if (this.cursors.up.isDown) this.cameras.main.scrollY -= speed;
    if (this.cursors.down.isDown) this.cameras.main.scrollY += speed;
}