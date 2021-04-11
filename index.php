<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Shiny</title>
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">

        <h1>Auto-Shiny</h1>
        <header>
            <nav>
                <ul>
                    <li data-element="hatch" class="active">Éclore</li>
                    <li data-element="release">Relacher</li>
                </ul>
            </nav>
        </header>
        <div class="element hatch active">

            <div class="sprite">
                <div class="default">
                    Choisissez un Pokémon
                </div>
            </div>
            <form id="search" action="">
                
                <input placeholder="Choisissez un pokémon" type="text" autocomplete="off" name="pokemon_choice" id="pokemon_choice"  value="<?= $_COOKIE['pokemon_name'] ?>">
                <div class="result hidden"></div>
                <label for="eggs">Nombre d'oeufs</label>
                <input type="number" name="eggs" id="eggs" value="<?= intval($_COOKIE['eggs']) ?>">
                <label for="usb">Port USB</label>
                <select name="usb" id="usb"></select>
                <input type="hidden" name="pokemon" id="pokemon" value="<?= $_COOKIE['id'] ?>">
                <input type="hidden" name="cycles"  id="cycles" value="<?= $_COOKIE['cycles'] ?>">
                <input type="hidden" name="command" value="pnh">
                <input type="hidden" name="pokemon_img" id="pokemon_img" value="<?= $_COOKIE['pokemon_img'] ?>">
                <button>Rechercher !</button>
            </form>
            <button class="stop">STOP</button>
        </div>
        <div class="element release">
            <form action="" id="release">
                <label for="eggs">Nombre de boîtes à relâcher</label>
                <input type="number" name="boxes" id="boxes" value="<?= round(intval($_COOKIE['eggs']) / 30) ?>">
                <p class="or">Ou</p>
                <label for="eggs">Nombre de pokémon à relâcher</label>
                <input type="number" name="eggs" id="release_eggs" value="<?= intval($_COOKIE['eggs']) ?>">
                <input type="hidden" name="command" value="release">
                <button>Relacher !</button>
            </form>
            <button class="stop">STOP</button>
        </div>
    </div>
    <script src="js/app.js"></script>
</body>
</html>