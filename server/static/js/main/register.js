App.init = () => {
  let solution = DOM.el(`#solution`)

  if (solution) {
    solution.focus()
  }
  else {
    let username = DOM.el(`#username`)

    if (username) {
      username.focus()
    }
  }
}