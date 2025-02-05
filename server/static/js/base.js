window.onload = () => {
  let captcha = document.querySelector(`#captcha-text`)
  captcha.placeholder = `Enter the captcha`
}

function validate() {
  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    if (!captcha.value.trim()) {
      return false
    }
  }

  let code = document.querySelector(`#code`)

  if (code) {
    if (!code.value.trim()) {
      return false
    }
  }

  let file = document.querySelector(`#file`)

  if (file.files.length > 0) {
    let file = file.files[0]

    if (file.size > max_size) {
      return false
    }
  }

  return true
}