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
let selectedEntityType = 'trap'; // Placeholder for the entity to place on click

function preload() {
    this.load.image('floor', 'assets/floor.png');
    this.load.image('wall', 'assets/wall.png');
    this.load.image('trap', 'assets/trap.png');
    this.load.image('start', 'assets/start.png');
    this.load.image('exit', 'assets/exit.png');
    this.load.image('dragon', 'assets/dragon.png');
    this.load.image('bomb', 'assets/bomb.png');
    this.load.image('hero', 'assets/goblinRight.png');
}

function create() {
    const scene = this;
    
    // Initial load
    refreshDungeon(scene);
        
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
    if (!grid || grid.length === 0) return;

    // Calculer les dimensions pour le centrage
    const gridWidth = Math.max(...grid.map(row => row.length));
    const gridHeight = grid.length;

    const dungeonTotalWidth = (gridWidth + gridHeight) * (TILE_WIDTH / 2);
    const dungeonTotalHeight = (gridWidth + gridHeight) * (TILE_HEIGHT / 2);

    const originX = (scene.sys.game.config.width - dungeonTotalWidth) / 2 + (dungeonTotalWidth/2);
    const originY = (scene.sys.game.config.height - dungeonTotalHeight) / 2;

    let minIsoX = Infinity, maxIsoX = -Infinity, minIsoY = Infinity, maxIsoY = -Infinity;

    grid.forEach(row => {
        row.forEach(cell => {
            const isoX = (cell.x - cell.y) * (TILE_WIDTH / 2) + originX;
            const isoY = (cell.x + cell.y) * (TILE_HEIGHT / 2) + originY;

            minIsoX = Math.min(minIsoX, isoX);
            maxIsoX = Math.max(maxIsoX, isoX);
            minIsoY = Math.min(minIsoY, isoY);
            maxIsoY = Math.max(maxIsoY, isoY);

            let floor = scene.add.image(isoX, isoY, 'floor').setOrigin(0.5, 1.0).setDepth(isoY);
            gridObjects.push(floor);

            // 2. Entités par dessus le sol
            let entityImage;
            switch(cell.type) {
                case 'WALL': entityImage = scene.add.image(isoX, isoY, 'wall'); break;
                case 'TRAP': entityImage = scene.add.image(isoX, isoY, 'trap'); break;
                case 'START': entityImage = scene.add.image(isoX, isoY, 'start'); break;
                case 'EXIT': entityImage = scene.add.image(isoX, isoY, 'exit'); break;
                case 'DRAGON': entityImage = scene.add.image(isoX, isoY, 'dragon'); break;
                case 'BOMBE': entityImage = scene.add.image(isoX, isoY, 'bomb'); break;
            }

            if (entityImage) {
                entityImage.setOrigin(0.5, 1.0).setDepth(isoY + 1);
                gridObjects.push(entityImage);
                floor.entityImage = entityImage; // Link entity to floor
            }

            // --- Hover and Click ---
            const hitArea = new Phaser.Geom.Polygon([
                32, 32,
                64, 48,
                32, 64,
                0, 48
            ]);
            floor.setInteractive(hitArea, Phaser.Geom.Polygon.Contains);
            floor.on('pointerover', () => {
                floor.setTint(0x868e96);
                if (floor.entityImage) {
                    floor.entityImage.setTint(0x868e96);
                }
            });
            floor.on('pointerout', () => {
                floor.clearTint();
                if (floor.entityImage) {
                    floor.entityImage.clearTint();
                }
            });
            floor.on('pointerdown', () => handleTileClick(cell));
        });
    });

    // --- Render Heroes ---
    heroes.forEach(hero => {
        const isoX = (hero.x - hero.y) * (TILE_WIDTH / 2) + originX;
        const isoY = (hero.x + hero.y) * (TILE_HEIGHT / 2) + originY;
        
        let heroImage = scene.add.image(isoX, isoY, 'hero').setOrigin(0.5, 1.0).setDepth(isoY + 2);
        gridObjects.push(heroImage);
    });
    
    // --- Center Camera ---
    const dungeonCenterX = minIsoX + (maxIsoX - minIsoX) / 2;
    const dungeonCenterY = minIsoY + (maxIsoY - minIsoY) / 2 - (TILE_HEIGHT * (gridHeight/2));
    
    scene.cameras.main.centerOn(dungeonCenterX, dungeonCenterY);
}

function handleTileClick(cell) {
    console.log(`Tile clicked at: (${cell.x}, ${cell.y})`);
    
    fetch('/api/command/placeEntity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            entity: selectedEntityType,
            x: cell.x,
            y: cell.y
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error('Failed to place entity: ' + text) });
        }
        console.log("Placement command sent successfully.");
        // The WebSocket 'dungeon_updated' message should trigger a refresh
    })
    .catch(error => {
        console.error('Error placing entity:', error);
    });
}

function update() {
    const speed = 8;
    if (this.cursors.left.isDown) this.cameras.main.scrollX -= speed;
    if (this.cursors.right.isDown) this.cameras.main.scrollX += speed;
    if (this.cursors.up.isDown) this.cameras.main.scrollY -= speed;
    if (this.cursors.down.isDown) this.cameras.main.scrollY += speed;
}
