App.init = () => {
  let username = DOM.el(`#username`)

  if (username) {
    username.focus()
  }
}