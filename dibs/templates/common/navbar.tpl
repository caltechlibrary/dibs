<nav class="navbar navbar-default navbar-light bg-light">
  <a href="{{base_url}}/">
    <img src="{{base_url}}/static/dibs-icon.svg" height="40rem"
         style="padding-left: 1rem; vertical-align: top">
  </a>
  <!-- Brand and toggle get grouped for better mobile display -->
  <div class="navbar-header ml-auto">
    <button type="button" class="navbar-toggler collapsed" aria-expanded="false"
            data-toggle="collapse" data-target="#navbar-menu">
      <span class="navbar-toggler-icon"></span>
    </button>
  </div>
  <!-- Collect the nav links, forms, and other content for toggling -->
  <div class="collapse navbar-collapse" id="navbar-menu">
    <ul class="nav navbar-nav text-right">
      %if logged_in:
        <li><a href="{{base_url}}/logout">Logout</a></li>
      %else:
        <li><a href="{{base_url}}/login">Staff login</a></li>
      %end
      %if staff_user:
        <li><a href="{{base_url}}/list">List Items</a></li>
      %end
      <li><a href="https://caltechlibrary.github.io/dibs/usage.html">Help</a></li>
      <li><a href="{{feedback_url}}">Give feedback</a></li>
      <li><a href="{{base_url}}/about">About</a></li>
    </ul>
  </div><!-- /.navbar-collapse -->
</nav>
