<?php 
$lang = substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2);

$lang = ($lang == 'fr') ? 'fr' : 'en';

require __DIR__ . '/lang/'.$lang.'.php';

?>
<html lang="<?= $lang ?>">
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
                    <li data-element="hatch" class="active"><?= $text['hatch'] ?></li>
                    <li data-element="release"><?= $text['release'] ?></li>
                </ul>
            </nav>
        </header>
        <div class="element hatch active">

            <div class="sprite">
                <div class="default">
                    <?= $text['choose_poke'] ?>
                </div>
            </div>
            <form id="search" action="">
                
                <input placeholder="<?= $text['choose_pkm'] ?>" type="text" autocomplete="off" name="pokemon_choice" id="pokemon_choice"  value="<?= $_COOKIE['pokemon_name'] ?>">
                <div class="result hidden"></div>
                <label for="eggs"><?= $text['egg_number'] ?></label>
                <input type="number" name="eggs" id="eggs" value="<?= intval($_COOKIE['eggs']) ?>">
                <label for="usb"><?= $text['usb_port'] ?></label>
                <select name="usb" class="usb"></select>
                <input type="hidden" name="pokemon" id="pokemon" value="<?= $_COOKIE['id'] ?>">
                <input type="hidden" name="cycles"  id="cycles" value="<?= $_COOKIE['cycles'] ?>">
                <input type="hidden" name="command" value="pnh">
                <input type="hidden" name="pokemon_img" id="pokemon_img" value="<?= $_COOKIE['pokemon_img'] ?>">
                <button><?= $text['search'] ?></button>
            </form>
            <button class="stop">STOP</button>
        </div>
        <div class="element release">
            <form action="" id="release">
                <label for="boxes"><?= $text['box_to_release'] ?></label>
                <input type="number" name="boxes" id="boxes" value="<?= round(intval($_COOKIE['eggs']) / 30) ?>">
                <p class="or"><?= $text['or'] ?></p>
                <label for="eggs"><?= $text['pkm_to_release'] ?></label>
                <input type="number" name="eggs" id="release_eggs" value="<?= intval($_COOKIE['eggs']) ?>">
                <input type="hidden" name="command" value="release">
                <select name="usb" class="usb"></select>

                <button><?= $text['release'] ?> !</button>
            </form>
            <button class="stop">STOP</button>
        </div>
    </div>
    <script src="js/app.js"></script>
</body>
</html>