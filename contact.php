<?php
    $firstname=$_POST['fname'];
    $lastname=$_POST['lname'];
    $email=$_POST['mail'];
    $phonenumber=$_POST['number'];
    $text=$_POST['text'];
    $conn = new mysqli('localhost','root','','voting');
    if($conn -> connect_error){
        die('Connection Failed : '. $conn->connect_error);
    }else{
        $stmt = $conn->prepare("INSERT INTO contact (fname,lname,mail,number,text) VALUES (?, ?, ?, ?, ?)");
        if (!$stmt) {
            die('Error in preparing statement: ' . $conn->error);
        }
        $stmt->bind_param("sssis",$firstname,$lastname,$email,$phonenumber,$text);
        if ($stmt->execute()) {
            header('location:home.html');
        } else {
            echo 'Error in executing statement: ' . $stmt->error;
        }
        $stmt->close();
        $conn->close();
    }
?>