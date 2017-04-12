from __future__ import absolute_import,unicode_literals

import re
from contextlib import contextmanager

import synapse.cortex as s_cortex
import synapse.daemon as s_daemon
import synapse.telepath as s_telepath

import synapse.lib.cmdr as s_cmdr
import synapse.cmds.cortex as s_cmds_cortex

from synapse.tests.common import *

class SynCmdCoreTest(SynTest):

    @contextmanager
    def getDmonCore(self):

        dmon = s_daemon.Daemon()
        core = s_cortex.openurl('ram:///')

        link = dmon.listen('tcp://127.0.0.1:0/')
        dmon.share('core00',core)
        port = link[1].get('port')
        prox = s_telepath.openurl('tcp://127.0.0.1/core00', port=port)

        s_scope.set('syn:test:link',link)
        #s_scope.set('syn:test:dmon',dmon)

        s_scope.set('syn:cmd:core',prox)

        yield prox

        prox.fini()
        core.fini()
        dmon.fini()

    def getCoreCmdr(self, core):
        outp = s_output.OutPutStr()
        return s_cmdr.getItemCmdr(core, outp=outp)

    def test_cmds_help(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('help')
            self.true( str(outp).find('List commands and display help output.') != -1 )

    def test_cmds_quit(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('quit')
            self.true( str(outp).find('o/') != -1 )

    def test_cmds_addnode(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('addnode inet:email visi@vertex.link')
            self.nn( core.getTufoByProp('inet:email','visi@vertex.link') )

    def test_cmds_addnode_noopts(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('addnode')
            self.nn(re.search('Examples:', str(outp)))

    def test_cmds_addtag(self):

        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)

            core.formTufoByProp('inet:email','visi@vertex.link')

            cmdr.runCmdLine('addtag woot inet:email="visi@vertex.link"')

            node = core.formTufoByProp('inet:email','visi@vertex.link')
            self.nn( node[1].get('*|inet:email|woot') )

    def test_cmds_addtag_nonodes(self):

        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)

            cmdr.runCmdLine('addtag woot inet:email="visi@vertex.link"')
            self.eq( str(outp).strip(), '0 nodes...')

    def test_cmds_addtag_noopts(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('addtag')
            self.nn(re.search('Examples:', str(outp)))

    def test_cmds_deltag(self):

        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)

            node = core.formTufoByProp('inet:email','visi@vertex.link')
            core.addTufoTag(node,'woot')

            cmdr.runCmdLine('deltag woot inet:email="visi@vertex.link"')

            node = core.getTufoByProp('inet:email','visi@vertex.link')
            self.none( node[1].get('*|inet:email|woot') )

    def test_cmds_deltag_nonodes(self):

        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)

            cmdr.runCmdLine('deltag woot inet:email="visi@vertex.link"')
            self.eq( str(outp).strip(), '0 nodes...')

    def test_cmds_deltag_noopts(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('deltag')
            self.nn(re.search('Examples:', str(outp)))

    def test_cmds_ask(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email','visi@vertex.link')
            resp = cmdr.runCmdLine('ask inet:email="visi@vertex.link"')
            self.eq( len(resp['data']), 1 )
            self.eq( str(outp).strip(), 'visi@vertex.link -')

    def test_cmds_ask_debug(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email','visi@vertex.link')
            resp = cmdr.runCmdLine('ask --debug inet:email="visi@vertex.link"')
            self.eq( len(resp['data']), 1 )

            outp = str(outp)
            terms = ('oplog', 'took', 'options', 'limits')

            for term in terms:
                self.nn(re.search(term, outp))

    def test_cmds_ask_props(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('inet:email','visi@vertex.link')
            resp = cmdr.runCmdLine('ask --props inet:email="visi@vertex.link"')
            self.eq( len(resp['data']), 1 )

            outp = str(outp)
            terms = ('fqdn = vertex.link', 'user = visi')

            for term in terms:
                self.nn(re.search(term, outp))

    def test_cmds_ask_multilift(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            core.formTufoByProp('str', 'hehe')
            core.formTufoByProp('inet:ipv4', 0)
            resp = cmdr.runCmdLine('ask str inet:ipv4')
            self.eq( len(resp['data']), 2 )

            outp = str(outp)
            terms = ('0.0.0.0 -', 'hehe -')

            for term in terms:
                self.nn(re.search(term, outp))

    def test_cmds_ask_noopts(self):
        with self.getDmonCore() as core:
            outp = s_output.OutPutStr()
            cmdr = s_cmdr.getItemCmdr(core, outp=outp)
            cmdr.runCmdLine('ask')
            self.nn(re.search('Examples:', str(outp)))