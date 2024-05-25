<?php
    $name=$_POST['name'];
    $email=$_POST['email'];
    $password=$_POST['pass'];
    $number = $_POST["number"];
    $conn = new mysqli('localhost','root','','voting');
    if($conn -> connect_error){
        die('Connection Failed : '. $conn->connect_error);
    }else{
        $stmt = $conn->prepare("INSERT INTO login (name,email,pass,number) VALUES (?, ?, ?, ?)");
        if (!$stmt) {
            die('Error in preparing statement: ' . $conn->error);
        }
        $stmt->bind_param("sssi",$name,$email,$password,$number);
        if ($stmt->execute()) {
            header('location:login2.php');
        } else {
            echo 'Error in executing statement: ' . $stmt->error;
        }
        $stmt->close();
        $conn->close();
    }
?>