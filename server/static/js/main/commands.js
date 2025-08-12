App.video_jump = () => {
  let video = DOM.el(`#video`)

  if (video) {
    if (video.paused) {
      App.video_jump_enabled = true
      video.play()
    }
    else {
      App.video_jump_action()
    }
  }
}

App.video_jump_action = () => {
  App.video_jump_enabled = false
  let duration = video.duration

  if (duration > 0) {
    let random_time = Math.random() * duration
    video.currentTime = random_time
  }
}

App.video_rewind = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.currentTime = Math.max(0, video.currentTime - 10)
    video.play()
  }
}

App.video_slow = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = Math.max(0.1, video.playbackRate - 0.1)
    video.play()
  }
}

App.video_fast = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = Math.min(10, video.playbackRate + 0.1)
    video.play()
  }
}

App.video_fade_in = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.volume = 0
    video.play()

    let fadeIn = setInterval(() => {
      if (video.volume < 1) {
        video.volume = Math.min(1, video.volume + 0.1)
      }
      else {
        clearInterval(fadeIn)
      }
    }, 300)
  }
}

App.video_fade_out = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.volume = 1

    let fadeOut = setInterval(() => {
      if (video.volume > 0) {
        video.volume = Math.max(0, video.volume - 0.1)
      }
      else {
        clearInterval(fadeOut)
        video.pause()
      }
    }, 300)
  }
}