<?php

$command = filter_input(INPUT_POST, 'command');
$pokemon = filter_input(INPUT_POST, 'pokemon');
$pokemon_name = filter_input(INPUT_POST, 'pokemon_choice');
$pokemon_img = filter_input(INPUT_POST, 'pokemon_img');
$cycles = filter_input(INPUT_POST, 'cycles');
$eggs = filter_input(INPUT_POST, 'eggs');
$usb = filter_input(INPUT_POST, 'usb');
$time = 50000;

if($pokemon) {
    setcookie('id', $pokemon, time() + $time);
}

if($eggs) {
    setcookie('eggs', $eggs, time() + $time);
}

if($cycles) {
    setcookie('cycles', $cycles, time() + $time);
}

if($pokemon_img) {
    setcookie('pokemon_img', $pokemon_img, time() + $time);
}


if($pokemon_name){
    setcookie('pokemon_name', $pokemon_name, time() + $time);
}

if($usb) {
    setcookie('usb', $usb, time() + $time);

}

$output=null;
$retval=null;

if($command == 'pnh'){
    $shellcommand = "sudo  /usr/bin/python3 shiny.py --port ".$_COOKIE['usb']." --command pnh --eggs ".$eggs." --cycles ".$cycles." 2>&1";
}

if($command == 'usb') {
    $shellcommand = 'sudo ls /dev/ttyUSB*';
}

if($command == 'stop') {
    $shellcommand = 'sudo pkill -f shiny.py && sudo  /usr/bin/python3 shiny.py --port '.$_COOKIE['usb'].' --command stop';
}


exec($shellcommand, $output, $retval);
echo json_encode($output);