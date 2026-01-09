const config = {
    type: Phaser.AUTO,
    backgroundColor: '#1a1a1a',
    parent: 'game-container', // Cible le div de gauche
    pixelArt: true,
    // Configuration de l'échelle pour s'adapter au div parent
    scale: {
        mode: Phaser.Scale.RESIZE,
        width: '100%',
        height: '100%'
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

const TILE_WIDTH = 64;
const TILE_HEIGHT = 32;

// Références globales
let gridObjects = [];
let selectedEntityType = 'trap';
let gameStarted = false;
let heroMoveInterval = null;
let gameEnded = false; // Nouvelle variable pour suivre la fin du jeu
let isInitialLoad = true; // Pour la gestion du rafraîchissement en cas de défaite

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
            refreshDungeon(scene, true);
        }
    };

    // Gestion de la sélection dans la sidebar
    const sidebarItems = document.querySelectorAll('.sidebar-item');

    // Sélection par défaut visuelle
    const defaultSelectedItem = document.getElementById(selectedEntityType);
    if (defaultSelectedItem) {
        defaultSelectedItem.classList.add('selected');
    }

    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            if (gameStarted || gameEnded) return; // Ne pas permettre la sélection si le jeu est démarré ou terminé
            sidebarItems.forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');
            selectedEntityType = item.id;
            console.log(`Selected entity type: ${selectedEntityType}`);
        });
    });

    // Gestion du bouton lancer
    const launchButton = document.getElementById('launch-button');
    launchButton.addEventListener('click', () => {
        if (!gameStarted && !gameEnded) { // Ne peut lancer que si le jeu n'est pas démarré ni terminé
            startGame(scene);
        }
    });

    // Gestion du bouton réinitialiser
    const resetButton = document.getElementById('reset-button');
    if(resetButton){
        resetButton.addEventListener('click', () => {
            resetGame(scene);
        });
    }

    // --- Import Dungeon UI handlers (simplified)
    const importBtn = document.getElementById('import-button');
    const statusEl = document.getElementById('import-status');

    function setImportStatus(msg, isError = false){
        if(!statusEl) return;
        statusEl.textContent = msg;
        statusEl.style.color = isError ? '#f88' : '#bff';
    }

    if(importBtn){
        importBtn.addEventListener('click', async () => {
            setImportStatus('Import en cours...');
            try{
                const resp = await fetch('/api/import_dungeon', { method: 'POST' });
                if(resp.ok){
                    setImportStatus('Donjon importé avec succès.');
                    
                    gridObjects.forEach(obj => {
                        if (obj && obj.destroy) {
                            obj.destroy();
                        }
                    });
                    gridObjects = [];
                    
                    // Réinitialiser le jeu et rafraîchir l'affichage
                    gameStarted = false;
                    gameEnded = false;
                    displayGameStatusMessage(''); // Cacher le message de statut
                    refreshDungeon(scene, true);
                    
                    // Réactiver la sidebar et les boutons
                    const sidebarItems = document.getElementById('sidebar-items');
                    sidebarItems.classList.remove('disabled');
                    
                    const launchButton = document.getElementById('launch-button');
                    launchButton.disabled = false;
                    launchButton.textContent = 'Lancer';
                    
                    const resetButton = document.getElementById('reset-button');
                    resetButton.disabled = false;
                }else{
                    const txt = await resp.text();
                    setImportStatus('Erreur serveur: ' + (txt || resp.statusText), true);
                }
            }catch(err){
                setImportStatus('Erreur lors de l\'import: ' + String(err), true);
            }
        });
    }
    // Gestion du bouton sauvegarder
    const saveButton = document.getElementById('save-button');
    saveButton.addEventListener('click', () => {
        console.log("Save button clicked");
        saveGame(scene);
    });

    // Écouteur pour redimensionnement de la fenêtre (optionnel avec RESIZE mais utile pour recentrer)
    scene.scale.on('resize', () => {
        refreshDungeon(scene, true);
    });
    
}

function updateSidebar(data) {
    const moneyElement = document.getElementById('money');
    if (moneyElement) {
        moneyElement.innerText = data.money;
    }

    const levelElement = document.getElementById('level');
    if (levelElement && data.level !== undefined) {
        levelElement.innerText = data.level;
    }

    const scoreElement = document.getElementById('score');
    if (scoreElement && data.score !== undefined) {
        scoreElement.innerText = data.score;
    }

    if (data.prices) {
        for (const item in data.prices) {
            const priceElement = document.querySelector(`#${item} .price`);
            if (priceElement) {
                priceElement.innerText = `${data.prices[item]}`;
            }
        }
    }
}

function displayGameStatusMessage(message, isError = false) {
    const statusMessageDiv = document.getElementById('game-status-message');
    if (statusMessageDiv) {
        statusMessageDiv.textContent = message;
        statusMessageDiv.style.display = message ? 'block' : 'none';
        statusMessageDiv.style.color = isError ? '#dc3545' : '#28a745'; // Rouge pour défaite, vert pour victoire
    }
}

function refreshDungeon(scene, forceRebuild = false) {
    console.log("refreshDungeon called with forceRebuild:", forceRebuild, "gridObjects.length:", gridObjects.length);
    displayGameStatusMessage(''); // Cache le message de statut à chaque rafraîchissement
    
    // Récupérer les nouvelles données du donjon (avec cache-busting)
    fetch('/api/dungeon?t=' + new Date().getTime())
        .then(res => res.json())
        .then(data => {
            console.log("Dungeon data received:", data);

            if (isInitialLoad) {
                isInitialLoad = false;
                if (data.tresorReached || data.allHeroesDead) {
                    console.log("Game ended state detected on initial load. Resetting game.");
                    resetGame(scene);
                    return; // resetGame will trigger a new refresh
                }
            }
            
            if (data.tresorReached) {
                gameEnded = true;
                displayGameStatusMessage('Défaite ! Le trésor a été pillé.', true);
                stopGame();
            } else if (data.allHeroesDead) {
                gameEnded = true;
                displayGameStatusMessage('Victoire ! Tous les héros sont morts.');
                stopGame();
                // Passer au niveau suivant après un court délai
                setTimeout(() => {
                    loadNextLevel(scene);
                }, 2000);
            } else {
                if (gridObjects.length === 0 || forceRebuild) {
                    console.log("Building complete grid");
                    buildIsoGrid(scene, data);
                } else {
                    // Juste mettre à jour les héros
                    console.log("Updating heroes only");
                    updateHeroesOnly(scene, data);
                }
            }
        })
        .catch(err => console.error("Erreur chargement donjon:", err));

    // Récupérer les données de la sidebar (argent, prix)
    fetch('/api/dungeon_data')
        .then(res => res.json())
        .then(data => {
            console.log("Sidebar data received:", data);
            updateSidebar(data);
        })
        .catch(err => console.error("Erreur chargement données sidebar:", err));
}

function buildIsoGrid(scene, data) {
    // Supprimer tous les objets de la grille existants avant de reconstruire
    gridObjects.forEach(obj => {
        if (obj.input) {
            obj.removeInteractive();
        }
        obj.destroy();
    });
    gridObjects = [];

    const grid = data.grid;
    const heroes = data.heros || [];
    if (!grid || grid.length === 0) return;

    // Calculer les dimensions pour le centrage
    const gridWidth = Math.max(...grid.map(row => row.length));
    const gridHeight = grid.length;

    const dungeonTotalWidth = (gridWidth + gridHeight) * (TILE_WIDTH / 2);
    const dungeonTotalHeight = (gridWidth + gridHeight) * (TILE_HEIGHT / 2);

    const originX = (scene.scale.width - dungeonTotalWidth) / 2 + (dungeonTotalWidth/2);
    const originY = (scene.scale.height - dungeonTotalHeight) / 2;

    grid.forEach(row => {
        row.forEach(cell => {
            const isoX = (cell.x - cell.y) * (TILE_WIDTH / 2) + originX;
            const isoY = (cell.x + cell.y) * (TILE_HEIGHT / 2) + originY;

            let floor = scene.add.image(isoX, isoY, 'floor').setOrigin(0.5, 1.0).setDepth(isoY);
            gridObjects.push(floor);

            // Entités
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
                floor.entityImage = entityImage;
            }

            // Interaction
            const hitArea = new Phaser.Geom.Polygon([
                32, 32, 64, 48, 32, 64, 0, 48
            ]);
            floor.setInteractive(hitArea, Phaser.Geom.Polygon.Contains);

            floor.on('pointerover', () => {
                floor.setTint(0x868e96);
                if (floor.entityImage) floor.entityImage.setTint(0x868e96);
            });

            floor.on('pointerout', () => {
                floor.clearTint();
                if (floor.entityImage) floor.entityImage.clearTint();
            });

            floor.on('pointerdown', () => {
                console.log("Tile clicked at:", cell.x, cell.y, "type:", cell.type, "selected:", selectedEntityType);
                handleTileClick(scene, cell);
            });
        });
    });

    // Heros - seulement si c'est une construction complète
    heroes.forEach(hero => {
        const isoX = (hero.x - hero.y) * (TILE_WIDTH / 2) + originX;
        const isoY = (hero.x + hero.y) * (TILE_HEIGHT / 2) + originY;

        let heroImage = scene.add.image(isoX, isoY, 'hero').setOrigin(0.5, 1.0).setDepth(isoY + 2);
        gridObjects.push(heroImage);
    });
}
   
function handleTileClick(scene, cell) {
    if (gameStarted || gameEnded) { // Ne pas permettre le placement si le jeu est démarré ou terminé
        console.log("Game started or ended, ignoring tile click");
        return;
    }
    
    console.log(`Tile clicked at: (${cell.x}, ${cell.y}) with entity ${selectedEntityType}, current cell type: ${cell.type}`);

    // On ne peut pas placer sur les cases de départ et de fin
    if (cell.type === 'START' || cell.type === 'EXIT') {
        console.log("Cannot place entity on start or exit tile.");
        return;
    }

    const requestBody = {
        type_entity: selectedEntityType,
        x: cell.x,
        y: cell.y
    };
    
    console.log("Sending request with body:", JSON.stringify(requestBody));

    fetch(`/api/place_entity/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
    .then(response => {
        console.log("Response status:", response.status);
        if (!response.ok) {
            return response.text().then(text => { 
                console.log("Error response:", text);
                throw new Error(text) 
            });
        }
        console.log("Entity placed successfully");
        // Si le placement est réussi, on rafraîchit l'affichage
        refreshDungeon(scene, true);
    })
    .catch(error => console.error('Error placing entity:', error));
}

function startGame(scene) {
    fetch('/api/start_simulation/')
        .then(res => res.json())
        .then(data => {
            if (data.simulation_started === "false" || data.simulation_started === false) {
                // Afficher l'erreur et ne pas démarrer le jeu
                alert(data.error || "Impossible de démarrer la simulation: un chemin est probablement bloqué.");
                // S'assurer que l'état du jeu est réinitialisé visuellement
                gameStarted = false;
                const launchButton = document.getElementById('launch-button');
                launchButton.disabled = false;
                launchButton.textContent = 'Lancer';

                const resetButton = document.getElementById('reset-button');
                resetButton.disabled = false;

                const sidebarItems = document.getElementById('sidebar-items');
                sidebarItems.classList.remove('disabled');

            } else {
                // Le démarrage a réussi, commencer la boucle de jeu
                gameStarted = true;
                gameEnded = false;
                displayGameStatusMessage(''); // Cache tout message précédent
                
                // Désactiver la sidebar
                const sidebarItems = document.getElementById('sidebar-items');
                sidebarItems.classList.add('disabled');
                
                // Désactiver le bouton lancer
                const launchButton = document.getElementById('launch-button');
                launchButton.disabled = true;
                launchButton.textContent = 'En cours...';
                
                // Désactiver le bouton réinitialiser
                const resetButton = document.getElementById('reset-button');
                resetButton.disabled = true;
                
                // Démarrer le déplacement automatique du héros toutes les 0.5 secondes
                heroMoveInterval = setInterval(() => {
                    moveHero(scene);
                }, 500);
                
                console.log("Game started - Hero moving automatically");
            }
        })
        .catch(error => {
            console.error('Error starting simulation:', error);
            alert('Erreur serveur lors du démarrage de la simulation.');
        });
}

function stopGame() {
    if (heroMoveInterval) {
        clearInterval(heroMoveInterval);
        heroMoveInterval = null;
    }
    gameStarted = false;

    // Réactiver les boutons de réinitialisation si le jeu est terminé
    const resetButton = document.getElementById('reset-button');
    if (resetButton) {
        resetButton.disabled = false;
    }
    // Lancer le bouton si le jeu est terminé et la victoire n'est pas acquise
    const launchButton = document.getElementById('launch-button');
    if (launchButton && !gameEnded) { // Réactiver seulement si pas en état de victoire/défaite
        launchButton.disabled = false;
        launchButton.textContent = 'Lancer';
    }
     // Réactiver la sidebar si le jeu est terminé
    const sidebarItems = document.getElementById('sidebar-items');
    if (sidebarItems && !gameEnded) { // Réactiver seulement si pas en état de victoire/défaite
        sidebarItems.classList.remove('disabled');
    }
}

function resetGame(scene) {
    stopGame(); // Arrêter le jeu si en cours

    gameStarted = false;
    gameEnded = false;
    displayGameStatusMessage(''); // Cacher le message de statut
    
    // Réactiver la sidebar
    const sidebarItems = document.getElementById('sidebar-items');
    sidebarItems.classList.remove('disabled');
    
    // Réactiver le bouton lancer
    const launchButton = document.getElementById('launch-button');
    launchButton.disabled = false;
    launchButton.textContent = 'Lancer';
    
    // Réactiver le bouton réinitialiser
    const resetButton = document.getElementById('reset-button');
    resetButton.disabled = false;
    
    // Réinitialiser la simulation côté serveur
    fetch('/api/reset_simulation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
        .then(data => {
            console.log('Simulation reset:', data);
            // Rafraîchir l'affichage pour montrer les héros au départ
            refreshDungeon(scene, true);
        })
    .catch(error => console.error('Error resetting simulation:', error));
    
    console.log("Game reset - Back to edit mode");
}

function saveGame(scene) {
    console.log("saveGame function called");
    
    // Demander le nom du fichier à l'utilisateur
    const filename = prompt("Entrez le nom du fichier de sauvegarde:", "dungeon_save");
    console.log("Filename:", filename);
    if (!filename) {
        console.log("Save cancelled by user");
        return;
    }

    // Récupérer la progression de campagne actuelle si disponible
    let campaignProgress = [];
    
    // Sauvegarder directement sans progression (l'API n'existe pas encore)
    performSave([]);

    function performSave(campaignProgress) {
        console.log("performSave called with progress:", campaignProgress);
        
        const saveData = {
            filename: filename,
            campaign_progress: campaignProgress
        };

        console.log("Save data:", saveData);

        // Désactiver le bouton pendant la sauvegarde
        const saveButton = document.getElementById('save-button');
        saveButton.disabled = true;
        saveButton.textContent = 'Sauvegarde...';

        console.log("Sending fetch request to /api/save_dungeon");
        
        fetch('/api/save_dungeon', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saveData)
        })
        .then(response => {
            console.log("Response received:", response);
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            console.log('Game saved successfully:', data);
            alert(`Donjon sauvegardé avec succès sous "${filename}.json"!`);
        })
        .catch(error => {
            console.error('Error saving game:', error);
            alert('Erreur lors de la sauvegarde: ' + error.message);
        })
        .finally(() => {
            // Réactiver le bouton
            saveButton.disabled = false;
            saveButton.textContent = 'Sauvegarder';
            console.log("Save process completed");
        });
    }
}
function moveHero(scene) {
    fetch('/api/move_hero', { // Changed from /api/start_simulation/ to /api/move_hero
        method: 'POST', // Changed to POST as per server definition
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json(); 
    })
    .then(data => {
        console.log('Hero moved:', data);
        if (data.simulation_started === "false") {
            alert("Chemin impossible")
            clearInterval(heroMoveInterval);
            heroMoveInterval = null
             // Réinitialiser l'état du jeu
    gameStarted = false;
    
    // Réactiver la sidebar
    const sidebarItems = document.getElementById('sidebar-items');
    sidebarItems.classList.remove('disabled');
    
    // Réactiver le bouton lancer
    const launchButton = document.getElementById('launch-button');
    launchButton.disabled = false;
    launchButton.textContent = 'Lancer';
    
    // Réactiver le bouton réinitialiser
    const resetButton = document.getElementById('reset-button');
    resetButton.disabled = false;

    
        }else{
            if (data.tresorReached) {
            gameEnded = true;
            displayGameStatusMessage('Défaite ! Le trésor a été pillé.', true);
            stopGame();
        } else if (data.allHeroesDead) {
            gameEnded = true;
            displayGameStatusMessage('Victoire ! Tous les héros sont morts.');
            stopGame();
            // Passer au niveau suivant après un court délai
            setTimeout(() => {
                loadNextLevel(scene);
            }, 2000);
        }else{
refreshDungeon(scene, false);
        }
        checkAllHeroesDead(scene);
        }

        
    })
    .catch(error => console.error('Error moving hero:', error));
}


function updateHeroesOnly(scene, data) {
    const heroes = data.heros || [];
    const grid = data.grid;
    if (!grid || grid.length === 0) return;

    // Calculer les dimensions pour le centrage
    const gridWidth = Math.max(...grid.map(row => row.length));
    const gridHeight = grid.length;

    const dungeonTotalWidth = (gridWidth + gridHeight) * (TILE_WIDTH / 2);
    const dungeonTotalHeight = (gridWidth + gridHeight) * (TILE_HEIGHT / 2);

    const originX = (scene.scale.width - dungeonTotalWidth) / 2 + (dungeonTotalWidth/2);
    const originY = (scene.scale.height - dungeonTotalHeight) / 2;

    // Supprimer uniquement les anciens héros
    const heroObjects = gridObjects.filter(obj => obj.texture.key === 'hero');
    heroObjects.forEach(obj => obj.destroy());
    
    // Filtrer les héros de la liste
    gridObjects = gridObjects.filter(obj => obj.texture.key !== 'hero');

    // Ajouter les nouveaux héros
    heroes.forEach(hero => {
        const isoX = (hero.x - hero.y) * (TILE_WIDTH / 2) + originX;
        const isoY = (hero.x + hero.y) * (TILE_HEIGHT / 2) + originY;

        let heroImage = scene.add.image(isoX, isoY, 'hero').setOrigin(0.5, 1.0).setDepth(isoY + 2);
        gridObjects.push(heroImage);
    });
}

function loadNextLevel(scene) {
    fetch('/api/next_level/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        console.log('Next level loaded:', data);
        
        // Attendre un peu que le serveur soit prêt
        setTimeout(() => {
            // Vider complètement la grille pour forcer la reconstruction
            gridObjects.forEach(obj => {
                if (obj && obj.destroy) {
                    obj.destroy();
                }
            });
            gridObjects = [];
            
            // Réinitialiser le jeu et rafraîchir l'affichage
            gameStarted = false;
            gameEnded = false;
            displayGameStatusMessage(''); // Cacher le message de statut
            refreshDungeon(scene, true);
            
            // Réactiver la sidebar et les boutons
            const sidebarItems = document.getElementById('sidebar-items');
            sidebarItems.classList.remove('disabled');
            
            const launchButton = document.getElementById('launch-button');
            launchButton.disabled = false;
            launchButton.textContent = 'Lancer';
            
            const resetButton = document.getElementById('reset-button');
            resetButton.disabled = false;
        }, 100);
    })
    .catch(error => console.error('Error loading next level:', error));
}


function checkAllHeroesDead(scene) {
    fetch('/api/dungeon?t=' + new Date().getTime())
        .then(res => res.json())
        .then(data => {
            const heroes = data.heros || [];
            if (heroes.length === 0) {
                // Tous les héros sont morts, passer au niveau suivant
                console.log("All heroes dead - moving to next level");
                
                // Arrêter le déplacement automatique
                if (heroMoveInterval) {
                    clearInterval(heroMoveInterval);
                    heroMoveInterval = null;
                }
                
                // Appeler la route next_level
                fetch('/api/next_level/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => { throw new Error(text) });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Next level loaded:', data);
                    
                    // Attendre un peu que le serveur soit prêt
                    setTimeout(() => {
                        // Vider complètement la grille pour forcer la reconstruction
                        gridObjects.forEach(obj => {
                            if (obj && obj.destroy) {
                                obj.destroy();
                            }
                        });
                        gridObjects = [];
                        
                        // Réinitialiser le jeu et rafraîchir l'affichage
                        gameStarted = false;
                        refreshDungeon(scene, true);
                        
                        // Réactiver la sidebar et les boutons
                        const sidebarItems = document.getElementById('sidebar-items');
                        sidebarItems.classList.remove('disabled');
                        
                        const launchButton = document.getElementById('launch-button');
                        launchButton.disabled = false;
                        launchButton.textContent = 'Lancer';
                        
                        const resetButton = document.getElementById('reset-button');
                        resetButton.disabled = false;
                    }, 100);
                })
                .catch(error => console.error('Error loading next level:', error));
            }
        })
        .catch(error => console.error('Error checking heroes status:', error));
}

function update() {
    const speed = 8;
    if (this.cursors.left.isDown) this.cameras.main.scrollX -= speed;
    if (this.cursors.right.isDown) this.cameras.main.scrollX += speed;
    if (this.cursors.up.isDown) this.cameras.main.scrollY -= speed;
    if (this.cursors.down.isDown) this.cameras.main.scrollY += speed;
}