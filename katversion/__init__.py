################################################################################
# Copyright (c) 2014-2018, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

from .version import get_version, build_info  # noqa: F401 (used in other packages)

# BEGIN VERSION CHECK
# Get package version when locally imported from repo or via -e develop install
__version__ = get_version(__path__[0])
# END VERSION CHECK
