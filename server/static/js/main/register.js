App.init = () => {
  let captcha = DOM.el(`#captcha`)

  if (captcha) {
    captcha.focus()
  }
  else {
    let username = DOM.el(`#username`)

    if (username) {
      username.focus()
    }
  }
}