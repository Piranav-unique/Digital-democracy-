<?php
    if(isset($_POST['email']) && isset($_POST['pass'])){
        function validate($data){
            $data = trim($data);
            $data = stripcslashes($data);
            $data = htmlspecialchars($data);
            return $data;
        }
    }
    $email = validate($_POST['email']);
    $pass = validate($_POST['pass']);
    $conn = new mysqli('localhost','root','','voting');

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    $stmt = $conn->prepare("SELECT * FROM login WHERE email = ? AND pass = ?");
    $stmt->bind_param("ss", $email, $pass);
    $stmt->execute();
    $result = $stmt->get_result();
    if($result->num_rows === 1){
        $row = $result->fetch_assoc();
        if($row['email'] === $email && $row['pass'] === $pass){
            header("Location: home.html");
            exit();
        }
        else{
            header("Location: login2.php?error= Email id or Password...");
            exit();
        }
    }
    else{
        header("Location: login2.php?error=Incorrect Email id or Password...");
        exit();
    }
?>