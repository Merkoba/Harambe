let clicked = false

window.onload = () => {
  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    captcha.placeholder = `Enter the captcha`
  }

  let image = document.querySelector(`#image`)

  if (image) {
    image.addEventListener(`click`, (e) => {
      let file = document.querySelector(`#file`)
      file.click()
    })

    image.addEventListener(`auxclick`, (e) => {
      if (e.button === 1) {
        if (e.ctrlKey) {
          window.location = `/admin`
        }
        else {
          window.location = `/list`
        }
      }
    })

    let file = document.querySelector(`#file`)

    if (file) {
      file.addEventListener(`change`, (e) => {
        clicked = false
        reflect_file()
      })
    }
  }

  document.addEventListener(`dragover`, (e) => {
    e.preventDefault()
  })

  document.addEventListener(`drop`, (e) => {
    e.preventDefault()
    let files = e.dataTransfer.files

    if (files && (files.length > 0)) {
      let file = document.querySelector(`#file`)
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

  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    if (!captcha.value.trim()) {
      return false
    }
  }

  let key = document.querySelector(`#key`)

  if (key) {
    if (!key.value.trim()) {
      return false
    }
  }

  let file = document.querySelector(`#file`)
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

  let comment = document.querySelector(`#comment`).value

  if (comment.length > vars.max_comment_length) {
    return false
  }

  clicked = true
  return true
}

function reflect_file() {
  let image = document.querySelector(`#image`)
  let file = document.querySelector(`#file`)
  let src = file.files[0]

  if (!is_image(src)) {
    image.src = `static/img/${vars.image_name}`
    return
  }

  let reader = new FileReader()

  reader.onload = (e) => {
    image.src = e.target.result
  }

  reader.readAsDataURL(src)
}

function is_image(file) {
  return file.type.match(`image/*`)
}