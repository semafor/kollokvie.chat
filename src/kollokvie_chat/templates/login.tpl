% rebase('base.html', title='Log in')
% setdefault('email', '')

<style type="text/css">
.errors li { color: "red"; }
</style>

% if defined('errors'):
<ul class="errors">
  % for error in errors:
    <li>{{error}}</li>
  % end
</ul>
% end

<form class="pure-form pure-form-stacked" action="/login" method="post">
    <fieldset>
        <legend>Log in to Kollokvie.chat</legend>

        <label for="email">Email</label>
        <input name="email" id="email" type="email" placeholder="ford@example.org" value="">

        <label for="password">Password</label>
        <input name="password" id="password" type="password" placeholder="Password">

        <button type="submit" class="pure-button pure-button-primary">Log in</button>
    </fieldset>
</form>


</html>
