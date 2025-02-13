let clicked = false

window.onload = () => {
  let captcha = DOM.el(`#captcha-text`)

  if (captcha) {
    captcha.placeholder = `Enter the captcha`
  }

  let image = DOM.el(`#image`)

  if (image) {
    DOM.ev(image, `click`, (e) => {
      if (e.shiftKey || e.ctrlKey || e.altKey) {
        reset_file()
        return
      }

      let file = DOM.el(`#file`)
      file.click()
    })

    DOM.ev(image, `auxclick`, (e) => {
      if (e.button === 1) {
        e.preventDefault()
        reset_file()
      }
    })

    let file = DOM.el(`#file`)

    if (file) {
      DOM.ev(file, `change`, (e) => {
        clicked = false
        reflect_file()
      })

      DOM.ev(file, `click`, (e) => {
        if (e.shiftKey || e.ctrlKey || e.altKey) {
          e.preventDefault()
          reset_file()
        }
      })

      DOM.ev(file, `auxclick`, (e) => {
        if (e.button === 1) {
          e.preventDefault()
          reset_file()
        }
      })
    }
  }

  DOM.ev(document, `dragover`, (e) => {
    e.preventDefault()
  })

  DOM.ev(document, `drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = DOM.el(`#file`)
      let dataTransfer = new DataTransfer()
      dataTransfer.items.add(files[0])
      file.files = dataTransfer.files
      reflect_file()
    }
  })
}

function validate() {
  if (clicked) {
    return false
  }

  if (!vars.is_user) {
    let captcha = DOM.el(`#captcha-text`)

    if (captcha) {
      if (!captcha.value.trim()) {
        return false
      }
    }
  }

  let file = DOM.el(`#file`)
  let file_length = file.files.length

  if (file_length === 0) {
    return false
  }

  if (file_length > 1) {
    return false
  }

  if (file.files[0].size > vars.max_size) {
    return false
  }

  let title = DOM.el(`#title`)

  if (title) {
    if (title.value.length > vars.max_title_length) {
      return false
    }
  }

  clicked = true
  return true
}

function reflect_file() {
  let title = DOM.el(`#title`)

  if (title) {
    title.focus()
  }

  let file = DOM.el(`#file`)
  let the_file = file.files[0]

  if (the_file.size > vars.max_size) {
    reset_file()
    alert(`That file is too big.`)
  }

  if (!is_image(the_file)) {
    reset_image()
    return
  }

  let reader = new FileReader()

  reader.onload = (e) => {
    image.src = e.target.result
  }

  reader.readAsDataURL(the_file)
}

function is_image(file) {
  return file.type.match(`image/*`)
}

function reset_file() {
  let file = DOM.el(`#file`)
  file.value = null
  reset_image()
}

function reset_image() {
  let image = DOM.el(`#image`)
  image.src = `static/img/${vars.image_name}`
}