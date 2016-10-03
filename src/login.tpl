<html>

<style type="text/css">
.errors li { color: "red"; }
</style>

<h1>Kollokvie.chat</h1>
<p>Please login</p>

% if defined('errors'):
<ul class="errors">
  % for error in errors:
    <li>{{error}}</li>
  % end
</ul>
% end

<form action="/login" method="post">
    Username: <input name="username" type="text" />
    Password: <input name="password" type="password" />
    <button type="submit">Login</button>
</form>

</html>
