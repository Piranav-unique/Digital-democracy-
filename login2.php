<!DOCTYPE html>
<html>
  <head lang="eng">
    <meta charset="UTF-8" />
    <meta name="description" content="Online Voting System" />
    <meta name="keywords" content="HTML, CSS, JavaScript" />
    <meta name="author" content="Piranav M.N,Yogesh T" />
    <title>Signup Page</title>
    <link rel="icon" href="logo-removebg-preview.png">
    <link rel="stylesheet" href="style.css" />
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"
    />
    <style>
      .input-box {
        position: relative;
      }
      .input-box input {
        width: 100%;
        padding-right: 40px;
      }
      .input-box .toggle-visibility {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: #ccc;
      }
    </style>
  </head>
  <body>
    <div class="wrapper">
      <form method="post" action="gotohome.php">
        <h1>Login</h1>
        <div class="input-box">
          <input type="email" placeholder="E-mail" name="email" required />
        </div>
        <div class="input-box">
          <input type="password" id="password" placeholder="Password" required name="pass"/>
          <i class="far fa-eye toggle-visibility" id="togglePassword" style="cursor: pointer;"></i>
        </div>
        <?php
                if (isset($_GET['error'])) {
                    $error = htmlspecialchars($_GET['error'], ENT_QUOTES, 'UTF-8');
                    echo "<span class='erro'>"."$error"."</span>";
                }
        ?>
        <button type="submit" class="btn">Login</button>
        <div class="register-link">
          <p>Are You an New User ?</p>
          <a href="signup.html">Sign Up </a>
        </div>
      </form>
    </div>
    <script>
      const togglePassword = document.querySelector('#togglePassword');
      const password = document.querySelector('#password');
      togglePassword.addEventListener('click', function (e) {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('fa-eye-slash');
      });
    </script>
  </body>
</html>
