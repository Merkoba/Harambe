window.onload = () => {
  let copy = document.querySelector(`#copy`)

  if (copy) {
    copy.addEventListener(`click`, () => {
      if (vars.mode === `upload`) {
        let loc = window.location
        let root = `${loc.protocol}//${loc.hostname}`

        if (loc.port) {
          root += `:${loc.port}`
        }

        navigator.clipboard.writeText(`${root}/${vars.data}`)
      }
    })
  }

  let new_tab = document.querySelector(`#new_tab`)

  if (new_tab) {
    new_tab.addEventListener(`click`, () => {
      if (vars.mode === `upload`) {
        window.open(vars.data, `_blank`)
      }
    })
  }
}