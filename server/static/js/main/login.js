DOM.ev(document, `DOMContentLoaded`, () => {
  App.init()
})

App.init = () => {
  let username = document.getElementById(`username`)

  if (username) {
    username.focus()
  }
}