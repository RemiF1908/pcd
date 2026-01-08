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

// Garder une référence aux objets de la grille pour les supprimer facilement
let gridObjects = [];

function preload() {
    this.load.image('floor', 'assets/floor.png');
    this.load.image('wall', 'assets/wall.png');
    this.load.image('trap', 'assets/trap.png');
    this.load.image('start', 'assets/start.png');
    this.load.image('exit', 'assets/exit.png');
    this.load.image('hero', 'assets/goblinRight.png'); // Assurez-vous d'avoir une image pour le héros
}

function create() {
    const scene = this;
    
    // Initial load
    refreshDungeon(scene);
        
    // Centrage de la caméra
    this.cameras.main.centerOn(0, 0);
    this.cursors = this.input.keyboard.createCursorKeys();

    // Connexion WebSocket
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        console.log("WebSocket connection established.");
    };

    ws.onmessage = (event) => {
        if (event.data === "dungeon_updated") {
            console.log("Dungeon update received. Refreshing...");
            refreshDungeon(scene);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket connection closed.");
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function refreshDungeon(scene) {
    // Supprimer les anciens objets
    gridObjects.forEach(obj => obj.destroy());
    gridObjects = [];

    // Récupérer les nouvelles données
    fetch('/api/dungeon')
        .then(res => res.json())
        .then(data => {
            buildIsoGrid(scene, data);
        })
        .catch(err => console.error("Erreur chargement donjon:", err));
}

function buildIsoGrid(scene, data) {
    const grid = data.grid;
    const heroes = data.heros || [];
    const originX = scene.sys.game.config.width / 2;
    const originY = 100;

    grid.forEach(row => {
        row.forEach(cell => {
            const isoX = (cell.x - cell.y) * (TILE_WIDTH / 2) + originX;
            const isoY = (cell.x + cell.y) * (TILE_HEIGHT / 2) + originY;

            let floor = scene.add.image(isoX, isoY, 'floor');
            floor.setOrigin(0.5, 1.0);
            floor.setDepth(isoY);
            gridObjects.push(floor);

            let entityImage = null;
            if (cell.type !== 'FLOOR') {
                 entityImage = scene.add.image(isoX, isoY, cell.type.toLowerCase());
                 entityImage.setOrigin(0.5, 1.0);
                 entityImage.setDepth(isoY + 1);
                 gridObjects.push(entityImage);
            }
        });
    });

    heroes.forEach(hero => {
        const isoX = (hero.x - hero.y) * (TILE_WIDTH / 2) + originX;
        const isoY = (hero.x + hero.y) * (TILE_HEIGHT / 2) + originY;
        
        let heroImage = scene.add.image(isoX, isoY, 'hero');
        heroImage.setOrigin(0.5, 1.0);
        heroImage.setDepth(isoY + 2); // Un peu plus haut pour être visible
        gridObjects.push(heroImage);
    });
}

function update() {
    const speed = 8;
    if (this.cursors.left.isDown) this.cameras.main.scrollX -= speed;
    if (this.cursors.right.isDown) this.cameras.main.scrollX += speed;
    if (this.cursors.up.isDown) this.cameras.main.scrollY -= speed;
    if (this.cursors.down.isDown) this.cameras.main.scrollY += speed;
}