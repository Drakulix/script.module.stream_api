def state(app_state):
    try:
        return _state[app_state]
    except KeyError:
        print "Unknown: "+str(app_state)
        return 32038

_state = {
    -1:      32039,#StateNotInstalled
    0:       32040,#'StateInvalid',
    1:      'StateUninstalled',
    #NaN:   'StateUpdateRequired',
    #tested values
    2:       32045, #preallocating (probably just preparing or update required)
    258:     32045, #preallocating
    1282:    32046, #downloading!
    260:     32043, #validating
    8196:    32042, #first time setup

    #from the https://github.com/lutris/lutris/blob/master/docs/steam.rst
    #sadly most of them seem not to be used anymore
    4:       32041,#'StateFullyInstalled',
    8:       32043,#'StateRunning',
    16:      32042,#'StateEncrypted',
    32:      32044,#'StateFilesMissing',
    64:      32045,#'StateAppRunning',
    128:     32046,#'StateFilesCorrupt',
    256:     32047,#'StateUpdateRunning',
    512:     32048,#'StateUpdatePaused',
    1024:    32049,#'StateUpdateStarted',
    2186:    32048,#updating!
    2048:    32050,#'StateUninstalling',
    4096:    32051,#'StateBackupRunning',
    65536:   32052,#'StateReconfiguring',
    131072:  32053,#'StateValidating',
    262144:  32054,#'StateAddingFiles',
    524288:  32055,#'StatePreallocating',
    1048576: 32056,#'StateDownloading',
    2097152: 32057,#'StateStaging',
    4194304: 32058,#'StateCommitting',
    8388608: 32059,#'StateUpdateStopping',
}
