App.fade_delay = 100
App.audio_context = null
App.pitch_node = null
App.reverb_node = null
App.reverb_enabled = false
App.bass_boost_node = null
App.bass_boost_enabled = false
App.bass_cut_enabled = false
App.current_pitch_step = 0
App.pitch_step_size = 1
App.current_audio_source = null
App.playback_step = 0.1
App.jump_popup_delay = 5000
App.rotate_popup_delay = 5000

App.show_video_commands = () => {
  App.setup_video_commands_opts(true)
}

App.show_image_commands = () => {
  App.setup_image_commands_opts(true)
}

App.video_jump = () => {
  let video = App.get_video()

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
  let video = App.get_video()

  if (video) {
    let duration = video.duration

    if (duration > 0) {
      let random_time = Math.random() * duration
      video.currentTime = random_time

      App.corner_msg({
        text: `Jumped to ${parseInt(random_time)}s`,
        delay: App.jump_popup_delay,
        on_click: () => {
          App.video_jump_action()
        },
      })
    }
  }
}

App.video_rewind = () => {
  let video = App.get_video()

  if (video) {
    video.currentTime = 0
    video.play()
  }
}

App.update_playback_title = (mode) => {
  let video = App.get_video()

  if (video) {
    let playback = video.playbackRate.toFixed(2).replace(/\.?0+$/, ``)
    let speed = DOM.el(`#speed_menu_title`)
    let pitch = DOM.el(`#pitch_menu_title`)

    if (speed) {
      if (mode === `speed`) {
        speed.innerText = `Speed: ${playback}x`
      }
      else {
        speed.innerText = `Speed`
      }
    }

    if (pitch) {
      if (mode === `pitch`) {
        pitch.innerText = `Pitch: ${playback}x`
      }
      else {
        pitch.innerText = `Pitch`
      }
    }
  }
}

App.playback_change = (mode, action) => {
  let video = App.get_video()

  if (!video) {
    return
  }

  let rate

  if (App.playback_rate_mode !== mode) {
    rate = 1.0
  }
  else {
    rate = video.playbackRate
  }

  if (action === `increase`) {
    video.playbackRate = Math.min(10, rate + App.playback_step)
  }
  else if (action === `decrease`) {
    video.playbackRate = Math.max(0.1, rate - App.playback_step)
  }

  App.update_playback_title(mode)
  App.playback_rate_mode = mode
}

App.increase_playback = (mode) => {
  App.playback_change(mode, `increase`)
}

App.decrease_playback = (mode) => {
  App.playback_change(mode, `decrease`)
}

App.video_slower = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.decrease_playback(`speed`)
  }
}

App.video_faster = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.increase_playback(`speed`)
  }
}

App.video_speed_reset = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    video.playbackRate = 1.0
    App.update_playback_title(`speed`)
  }
}

App.video_fade_in = () => {
  let video = App.get_video()

  if (video) {
    video.volume = 0
    video.play()

    let fadeIn = setInterval(() => {
      if (video.volume < 1) {
        video.volume = Math.min(1, video.volume + 0.02)
      }
      else {
        clearInterval(fadeIn)
      }
    }, App.fade_delay)
  }
}

App.video_fade_out = () => {
  let video = App.get_video()

  if (video) {
    video.volume = 1

    let fadeOut = setInterval(() => {
      if (video.volume > 0) {
        video.volume = Math.max(0, video.volume - 0.02)
      }
      else {
        clearInterval(fadeOut)
        video.pause()
      }
    }, App.fade_delay)
  }
}

App.setup_audio_context = (video) => {
  if (!App.audio_context) {
    try {
      App.audio_context = new (window.AudioContext || window.webkitAudioContext)()
    }
    catch (e) {
      return false
    }
  }

  if (App.audio_context.state === `suspended`) {
    App.audio_context.resume()
  }

  if (!App.pitch_node || (video.audioSource !== App.current_audio_source)) {
    try {
      if (App.current_audio_source) {
        App.current_audio_source.disconnect()
      }

      let source = App.audio_context.createMediaElementSource(video)
      App.current_audio_source = source
      App.pitch_node = App.audio_context.createGain()

      if (!App.reverb_node) {
        App.create_reverb_node()
      }

      if (!App.bass_boost_node) {
        App.create_bass_boost_node()
      }

      source.connect(App.pitch_node)
      App.pitch_node.connect(App.bass_boost_node.input)
      App.bass_boost_node.output.connect(App.reverb_node.input)
      App.reverb_node.output.connect(App.audio_context.destination)
      video.audioSource = source
    }
    catch (e) {
      if (e.name === `InvalidStateError`) {
        return true
      }

      return false
    }
  }

  return true
}

App.video_pitch_up = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(false)
    App.increase_playback(`pitch`)
  }
}

App.video_pitch_down = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(false)
    App.decrease_playback(`pitch`)
  }
}

App.video_pitch_reset = () => {
  let video = App.get_video()

  if (video) {
    App.set_video_preserve_pitch(true)
    App.current_pitch_step = 0
    video.playbackRate = 1.0
    App.update_playback_title(`pitch`)
  }
}

App.set_video_preserve_pitch = (value) => {
  let video = App.get_video()

  if (video) {
    try {
      if (`preservesPitch` in video) {
        video.preservesPitch = value
      }

      if (`mozPreservesPitch` in video) {
        video.mozPreservesPitch = value
      }

      if (`webkitPreservesPitch` in video) {
        video.webkitPreservesPitch = value
      }
    }
    catch (e) {
      App.print_error(`Could not set pitch flag:`, e)
    }
  }
}

App.create_reverb_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let ac = App.audio_context
    let convolver = ac.createConvolver()
    let dry_gain = ac.createGain()
    let wet_gain = ac.createGain()
    let mix_gain = ac.createGain()
    let output_gain = ac.createGain()

    let pre_delay = ac.createDelay(1.0)
    pre_delay.delayTime.value = 0.03

    let lowpass = ac.createBiquadFilter()
    lowpass.type = `lowpass`
    lowpass.frequency.value = 6500
    lowpass.Q.value = 0.7

    let comp = ac.createDynamicsCompressor()
    comp.threshold.value = -18
    comp.knee.value = 20
    comp.ratio.value = 2
    comp.attack.value = 0.003
    comp.release.value = 0.25

    App.create_impulse_response(convolver)

    convolver.normalize = true
    dry_gain.gain.value = 1.0
    wet_gain.gain.value = 0.0
    mix_gain.gain.value = 1.0
    output_gain.gain.value = 1.0

    App.reverb_node = {
      input: ac.createGain(),
      convolver,
      pre_delay,
      lowpass,
      dry: dry_gain,
      wet: wet_gain,
      mix: mix_gain,
      comp,
      output: output_gain,
    }

    App.reverb_node.input.connect(App.reverb_node.dry)
    App.reverb_node.input.connect(App.reverb_node.pre_delay)
    App.reverb_node.pre_delay.connect(App.reverb_node.convolver)
    App.reverb_node.convolver.connect(App.reverb_node.lowpass)
    App.reverb_node.lowpass.connect(App.reverb_node.wet)
    App.reverb_node.dry.connect(App.reverb_node.mix)
    App.reverb_node.wet.connect(App.reverb_node.mix)
    App.reverb_node.mix.connect(App.reverb_node.comp)
    App.reverb_node.comp.connect(App.reverb_node.output)
  }
  catch (e) {
    App.print_error(`Could not create reverb node:`, e)
  }
}

App.create_impulse_response = (convolver) => {
  try {
    let ac = App.audio_context
    let sample_rate = ac.sampleRate

    let seconds = 3.0
    let length = Math.floor(sample_rate * seconds)
    let impulse = ac.createBuffer(2, length, sample_rate)

    let earlyTimes = [0.007, 0.013, 0.021, 0.033]
    let earlyGains = [0.6, 0.45, 0.32, 0.22]

    for (let channel = 0; channel < 2; channel++) {
      let data = impulse.getChannelData(channel)

      for (let j = 0; j < earlyTimes.length; j++) {
        let t = earlyTimes[j] + (channel === 0 ? 0.000 : 0.0015)
        let idx = Math.floor(t * sample_rate)
        if (idx < length) {
          let gain = earlyGains[j]

          for (let k = -8; k <= 8; k++) {
            let p = idx + k

            if ((p >= 0) && (p < length)) {
              let window = 1 - Math.abs(k) / 8
              data[p] += gain * window * 0.04
            }
          }
        }
      }

      let decay = 3.5

      for (let i = 0; i < length; i++) {
        let t = i / length
        let env = Math.pow(1 - t, decay)
        let noise = ((Math.random() * 2) - 1) * env * 0.6
        data[i] += noise
      }

      for (let i = Math.floor(length * 0.85); i < length; i++) {
        let fade = (length - i) / (length * 0.15)
        data[i] *= fade
      }
    }

    convolver.buffer = impulse
  }
  catch (e) {
    App.print_error(`Could not create impulse response:`, e)
  }
}

App.create_bass_boost_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let ac = App.audio_context
    let input_gain = ac.createGain()
    let output_gain = ac.createGain()

    let bass_filter = ac.createBiquadFilter()
    bass_filter.type = `lowshelf`
    bass_filter.frequency.value = 320
    bass_filter.gain.value = 0
    bass_filter.Q.value = 1.0

    let highpass = ac.createBiquadFilter()
    highpass.type = `highpass`
    highpass.frequency.value = 40
    highpass.Q.value = 0.7

    input_gain.gain.value = 1.0
    output_gain.gain.value = 1.0

    App.bass_boost_node = {
      input: input_gain,
      bass_filter,
      highpass,
      output: output_gain,
    }

    App.bass_boost_node.input.connect(App.bass_boost_node.highpass)
    App.bass_boost_node.highpass.connect(App.bass_boost_node.bass_filter)
    App.bass_boost_node.bass_filter.connect(App.bass_boost_node.output)
  }
  catch (e) {
    App.print_error(`Could not create bass boost node:`, e)
  }
}

App.set_bass_gain = (gain_db) => {
  if (!App.bass_boost_node || !App.audio_context) {
    return
  }

  let ac = App.audio_context
  let now = ac.currentTime
  let clamped_gain = Math.max(-12, Math.min(12, gain_db))

  App.bass_boost_node.bass_filter.gain.setTargetAtTime(clamped_gain, now, 0.01)
}

App.set_reverb_mix = (mix) => {
  if (!App.reverb_node || !App.audio_context) {
    return
  }

  let ac = App.audio_context
  let t = Math.max(0, Math.min(1, mix)) * Math.PI / 2
  let dryLevel = Math.cos(t)
  let wetLevel = Math.sin(t)
  let now = ac.currentTime

  App.reverb_node.dry.gain.setTargetAtTime(dryLevel, now, 0.01)
  App.reverb_node.wet.gain.setTargetAtTime(wetLevel, now, 0.01)
}

App.video_reverb_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.reverb_node) {
      App.button_highlight(`video_commands_opts_reverb`)
      App.reverb_enabled = true
      App.set_reverb_mix(0.55)
    }
  }
}

App.video_reverb_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.reverb_node) {
      App.button_highlight(`video_commands_opts_reverb`, false)
      App.reverb_enabled = false
      App.set_reverb_mix(0.0)
    }
  }
}

App.video_reverb_toggle = () => {
  if (App.reverb_enabled) {
    App.video_reverb_off()
  }
  else {
    App.video_reverb_on()
  }
}

App.video_bass_boost_toggle = () => {
  App.video_bass_cut_off()

  if (App.bass_boost_enabled) {
    App.video_bass_boost_off()
  }
  else {
    App.video_bass_boost_on()
  }
}

App.video_bass_boost_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.bass_boost_node) {
      App.button_highlight(`video_commands_opts_bass_boost`)
      App.bass_boost_enabled = true
      App.set_bass_gain(6)
    }
  }
}

App.video_bass_boost_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.bass_boost_node) {
      App.button_highlight(`video_commands_opts_bass_boost`, false)
      App.bass_boost_enabled = false
      App.set_bass_gain(0)
    }
  }
}

App.video_bass_cut_toggle = () => {
  App.video_bass_boost_off()

  if (App.bass_cut_enabled) {
    App.video_bass_cut_off()
  }
  else {
    App.video_bass_cut_on()
  }
}

App.video_bass_cut_on = () => {
  let video = App.get_video()

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.bass_boost_node) {
      App.button_highlight(`video_commands_opts_bass_cut`)
      App.bass_cut_enabled = true
      App.set_bass_gain(-8)
    }
  }
}

App.video_bass_cut_off = () => {
  let video = App.get_video()

  if (video) {
    if (App.bass_boost_node) {
      App.button_highlight(`video_commands_opts_bass_cut`, false)
      App.bass_cut_enabled = false
      App.set_bass_gain(0)
    }
  }
}

App.image_rotate = (direction) => {
  App.show_modal_image()
  let image = DOM.el(`#modal_image`)

  if (!image) {
    return
  }

  if (!image.dataset.rotation) {
    image.dataset.rotation = 0
  }

  let currentRotation = parseInt(image.dataset.rotation)

  if (direction === `clockwise`) {
    currentRotation += 90
  }
  else if (direction === `counterclockwise`) {
    currentRotation -= 90
  }

  image.dataset.rotation = currentRotation
  image.style.transform = `rotate(${currentRotation}deg)`
  image.style.transformOrigin = `center center`
  image.style.transition = `transform 0.3s ease`

  App.corner_msg({
    text: `Click to rotate more`,
    delay: App.rotate_popup_delay,
    on_click: () => {
      App.image_rotate(direction)
    },
  })
}