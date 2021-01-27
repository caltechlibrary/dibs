<!DOCTYPE html>
<html lang="en">

  <head>
    <title>Welcome to Caltech DIBS</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    <style>
     ::-webkit-input-placeholder                   { color: #bbb; }
     html .form-control::placeholder               { color: #bbb; }
     html .form-control::-webkit-input-placeholder { color: #bbb; }
     html .form-control:-moz-placeholder           { color: #bbb; }
     html .form-control::-moz-placeholder          { color: #bbb; }
     html .form-control:-ms-input-placeholder      { color: #bbb; }
    </style>
  </head>
  
  <body>
    <div class="container text-center">
      <div class="row my-5">
        <div class="col">
        <h1 class="mx-auto text-center" style="color: #FF6C0C">
            Welcome to Caltech DIBS
          </h1>
          <h2 class="mx-auto my-3 text-center text-info font-italic">
            The Caltech <strong>Di</strong>gital <strong>B</strong>orrowing <strong>S</strong>ystem
          </h2>
          <p class="my-3"><strong>Caltech DIBS</strong> is an implementation of <a target="_blank" href="https://controlleddigitallending.org">Controlled Digital Lending</a>, allowing members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats.  The system was implemented in the year 2021 to help Caltech students and faculty during the global <a target="_blank" href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019">COVID-19 pandemic.</a> Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff.</p>
        </div>
      </div>
      <div class="row justify-content-center">
        <div class="col-md-4 col-md-offset-4">
          <form action="/login" method="post">
            <input class="my-1" name="email" type="text" placeholder="User" required autofocus/>
            <input class="my-1" name="password" type="password" placeholder="Password" required/><br>
            <input class="btn btn-primary my-2" value="Login" type="submit" />
          </form>
        </div>
      </div>
    </div>
  </body>
</html>
