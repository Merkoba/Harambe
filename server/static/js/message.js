window.onload = () => {
  let copy = document.getElementById(`copy`)

  if (copy) {
    copy.addEventListener(`click`, () => {
      if (mode === `upload`) {
        let loc = window.location
        let root = `${loc.protocol}//${loc.hostname}`

        if (loc.port) {
          root += `:${loc.port}`
        }

        navigator.clipboard.writeText(`${root}/${data}`)
      }
    })
  }

  let new_tab = document.getElementById(`new_tab`)

  if (new_tab) {
    new_tab.addEventListener(`click`, () => {
      if (mode === `upload`) {
        window.open(data, `_blank`)
      }
    })
  }
}