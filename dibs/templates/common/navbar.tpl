<nav class="navbar navbar-light bg-light">
  <a href="{{base_url}}/">
    <img src="{{base_url}}/static/dibs-icon.svg" height="40rem">

  </a>
  <!-- Brand and toggle get grouped for better mobile display -->
  <div class="navbar-header ml-auto">
    <button type="button" class="navbar-toggler collapsed"
            data-toggle="collapse" data-target="#navbar-menu"
            aria-expanded="false">
      <span class="navbar-toggler-icon"></span>
    </button>
  </div>
  <!-- Collect the nav links, forms, and other content for toggling -->
  <div class="collapse navbar-collapse" id="navbar-menu">
    <ul class="nav navbar-nav text-right">
      %if logged_in:
        <form action="{{base_url}}/logout" method="POST">
          <input class="link-not-button" type="submit" name="edit" value="Logout"/>
        </form>
      %end
      %if staff_user:
        <li><a href="{{base_url}}/list">List Items</a></li>
        <li><a href="{{base_url}}/stats">Loan statistics</a></li>
      %end
      <li><a href="https://caltechlibrary.github.io/dibs/usage.html">Help</a></li>
      <li><a href="{{feedback_url}}">Give feedback</a></li>
      <li><a href="{{base_url}}/about">About</a></li>
    </ul>
  </div><!-- /.navbar-collapse -->
</nav>
