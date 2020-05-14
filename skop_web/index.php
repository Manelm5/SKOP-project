<?php
require_once(realpath(dirname(__FILE__) . '/constants.php'));
header('X-XSS-Protection:0');
if(isset($_GET['action'])){
  $action = $_GET['action'];
}
session_start();

switch($action){
  case 'principal':
    include CONTROLLERS.'principal.php';
    break;
 case 'registrar':
    include CONTROLLERS.'registre.php';
    break;
  case 'login':
    include CONTROLLERS.'login.php';
    break;
  default:
    include CONTROLLERS.'principal.php';
    break;
}

?>